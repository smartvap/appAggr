import selenium
from selenium import webdriver
import time
import cx_Oracle
import re
import base64
from PIL import Image
import np
import cv2
from io import BytesIO

# 字典表
# lnkPrefix 链接前缀
# 
dict = {
    'lnkPrefix': 'https://www.ppkao.com/tiku/shiti/',
    'lnkSuffix': '.html',
    'idleTime': '10',
    'db_user': 'c##k8s',
    'db_pass': 'k8s',
    'db_tns': 'cdb1'
}

# 属性、xpath映射关系
mapPropXPath = {
    'quesBank': '/html/body/div[3]/div[2]/div/div[1]/span',
    'quesType': '/html/body/div[4]/div[2]/div[2]/div[2]/i',
    'quesCont': '/html/body/div[4]/div[2]/div[2]/div[2]/strong',
    'opts': '/html/body/div[4]/div[2]/div[2]/div[2]/p[2]',
    'ansTxt': '/html/body/div[4]/div[2]/div[2]/div[3]/div[1]/span',
    'ansBtn': '/html/body/div[4]/div[2]/div[2]/div[3]/a[1]',
    'wxLogin': '//iframe[contains(@src, "login/wx_follow.aspx")]',
    'ansImgBase64': '//img[contains(@src, "data:image")]',
    'interpretation': '//*[@id="content"]/div[3]/p'
}

# 问题对象：quesObj，属性值是不确定的
# 属性名称：链接序号(snLink)、题库名称(quesBank)、题目类型(quesType)、问题(quesCont)、选项(opts)...
quesObj = {
}

# 解析问题数据
# 参数：
#  1、driver对象
#  2、元素xpath路径
#  3、元素属性：src、innerText等
#  4、数据保存到的临时对象
#  5、临时对象的属性名
#  6、循环次数，0为无穷次
def parseQues(drv, xpath, attrName, quesObj, propName, nCycle):
    driver.implicitly_wait(10)                          # 对所有元素都显示等待5s
    n = 1                                               # 循环次数
    while True:                                         # 若10s还不够，则循环等待
        try:
            elem = drv.find_element_by_xpath(xpath)     # 根据xpath搜索元素
            propVal = drv.execute_script('return arguments[0].' + attrName + ';', elem)
            propVal = propVal.replace('\xa0', '')
            quesObj[propName] = propVal                 # 写入映射对象
            break
        except selenium.common.exceptions.NoSuchElementException:
            print('未找到元素 ' + propName + ' , 10s后重试 ...')
        except selenium.common.exceptions.WebDriverException:
            print("Other element would receive the click.")
        if nCycle > 0 and n >= nCycle:
            quesObj[propName] = ''
            break
        if n > 3:
            drv.get(dict['lnkPrefix'] + str(i) + dict['lnkSuffix'])
            time.sleep(10)
            drv.execute_script("ViewAnswers('//api.ppkao.com/mnkc/tiku/?id=" + str(i) + "','432')")
            

# 页面切换到另一个页面
def doSwitchPage(drv):
    try:
        currHwnd = drv.current_window_handle
        for handle in drv.window_handles:
            if handle != currHwnd:
                drv.switch_to.window(handle)
    except selenium.common.exceptions.NoSuchWindowException:
        if drv.window_handles and drv.window_handles.__len__() > 0:
            drv.switch_to.window(drv.window_handles[0])

# 关闭其他页面
def closeOtherPages(drv):
    try:
        currHwnd = drv.current_window_handle
        handles = drv.window_handles
        for handle in handles:
            if handle != currHwnd:
                drv.switch_to.window(handle)
                drv.close()
        drv.switch_to.window(currHwnd)
    except:
        print("")

# 图像格式转换

# 图像识别

# 数据库初始化
def db_init():
	try:
		conn = cx_Oracle.connect(dict['db_user'], dict['db_pass'], dict['db_tns'])
		cursor = conn.cursor()
		cursor.execute('CREATE TABLE t_ppk_ques ' +
		'(' +
		'  sn_lnk     NUMBER(16) NOT NULL,' +
		'  ques_bank  VARCHAR2(512) NOT NULL,' +
		'  ques_type  VARCHAR2(512) NOT NULL,' +
		'  ques_cont  VARCHAR2(4000) NOT NULL,' +
		'  opts       VARCHAR2(4000),' +
		'  ans_img_c  CLOB,' +
		'  ans_bin_c  CLOB,' +
		'  interpret  CLOB' +
		')' +
		'PARTITION BY RANGE (sn_lnk)' +
		'(' +
		'  PARTITION p_1 VALUES LESS THAN (1000000)' +
		'    TABLESPACE users' +
		'    PCTFREE 10' +
		'    INITRANS 40' +
		'    MAXTRANS 255' +
		'    STORAGE' +
		'    (' +
		'      INITIAL 1M' +
		'      NEXT 2M' +
		'      MINEXTENTS 1' +
		'      MAXEXTENTS UNLIMITED' +
		'      PCTINCREASE 0' +
		'    ),' +
		'  PARTITION p_2 VALUES LESS THAN (2000000)' +
		'    TABLESPACE users' +
		'    PCTFREE 10' +
		'    INITRANS 40' +
		'    MAXTRANS 255' +
		'    STORAGE' +
		'    (' +
		'      INITIAL 1M' +
		'      NEXT 2M' +
		'      MINEXTENTS 1' +
		'      MAXEXTENTS UNLIMITED' +
		'      PCTINCREASE 0' +
		'    ),' +
		'  PARTITION p_max VALUES LESS THAN (MAXVALUE)' +
		'    TABLESPACE users' +
		'    PCTFREE 10' +
		'    INITRANS 40' +
		'    MAXTRANS 255' +
		'    STORAGE' +
		'    (' +
		'      INITIAL 1M' +
		'      NEXT 2M' +
		'      MINEXTENTS 1' +
		'      MAXEXTENTS UNLIMITED' +
		'      PCTINCREASE 0' +
		'    )' +
		')')
		cursor.execute('CREATE UNIQUE INDEX pk_t_ques ON t_ppk_ques (sn_lnk) TABLESPACE users')
		cursor.execute('CREATE BITMAP INDEX idx_t_ques_bank ON t_ppk_ques(ques_bank) TABLESPACE users LOCAL')
		cursor.execute('CREATE BITMAP INDEX idx_t_ques_type ON t_ppk_ques(ques_type) TABLESPACE users LOCAL')
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.sn_lnk IS '问题序号'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.ques_bank IS '题库名称'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.ques_type IS '问题类型'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.ques_cont IS '题干'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.opts      IS '选项'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.ans_img_c IS '答案图片BASE64编码（原始）'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.ans_bin_c IS '答案图片BASE64编码（灰度处理）'")
		cursor.execute("COMMENT ON COLUMN t_ppk_ques.interpret IS '诠释'")
		cursor.close()
		conn.close()
		del cursor
		del conn
	except cx_Oracle.DatabaseError:
		print('')

# 数据保存
# sn：问题序号
# ques：问题对象
def save(sn, ques):
    try:
        conn = cx_Oracle.connect(dict['db_user'], dict['db_pass'], dict['db_tns'])
        cursor = conn.cursor()
        sql = 'INSERT INTO t_ppk_ques(sn_lnk, ques_bank, ques_type, ques_cont, ' +\
            'opts, ans_img_c, ans_bin_c, interpret) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)';
        cursor.prepare(sql)
        cursor.execute(sql, (sn, ques['quesBank'], ques['quesType'], ques['quesCont'], \
                             ques['opts'], ques['ansImgBase64'], ques['ansGrayBase64'], ques['interpretation']))
        conn.commit()
        cursor.close()
        conn.close()
        del sql
        del cursor
        del conn
    except cx_Oracle.DatabaseError:
        print('数据库访问异常')

# 显示答案灰度图象版本
def dispAnsGray(sn):
	try:
		conn = cx_Oracle.connect(dict['db_user'], dict['db_pass'], dict['db_tns'])
		cursor = conn.cursor()
		sql = 'SELECT ans_bin_c FROM t_ppk_ques WHERE sn_lnk = :1'
		cursor.prepare(sql)
		cursor.execute(sql, [ sn ])
		for rec in cursor:
			base64_str = rec[0].read()
		cursor.close()
		conn.close()
		del sql
		del cursor
		del conn
		base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
		byte_data = base64.b64decode(base64_data)
		image_data = BytesIO(byte_data)
		img = Image.open(image_data)
		img.show()
	except cx_Oracle.DatabaseError:
		print('')

# pip install pillow
# pip install np
# pip install numpy
# pip install opencv-python


# 对原始图像Base64编码解码、灰度处理、再转换为Base64编码返回
# Base64编码入库CLOB字段时，不能带b头部，应去掉。
def getGrayBase64(base64_str):
	base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
	byte_data = base64.b64decode(base64_data)
	imgArr = np.frombuffer(byte_data, np.uint8)
	img = cv2.imdecode(imgArr, cv2.COLOR_BGR2RGB)
	ret, thresh1 = cv2.threshold(img[:,:,0], 90, 255, cv2.THRESH_BINARY)
	img = Image.fromarray(thresh1)
	output_buffer = BytesIO()
	img.save(output_buffer, format = 'JPEG')
	byte_data = output_buffer.getvalue()
	base64_str = base64.b64encode(byte_data)
	return base64_str.decode('ascii')

# 主循环
driver = webdriver.Chrome()
for i in range(1, 2):
	closeOtherPages(driver)
	print('只保留一个页签...')
	driver.get(dict['lnkPrefix'] + str(i) + dict['lnkSuffix'])
	print('打开问题' + str(i) + '...')
	if not 'quesObj' in locals():
		quesObj = {}
	parseQues(driver, mapPropXPath['quesBank'], 'innerText', quesObj, 'quesBank', 0)
	print('获取题库名称...')
	parseQues(driver, mapPropXPath['quesType'], 'innerText', quesObj, 'quesType', 0)
	print('获取问题类型...')
	parseQues(driver, mapPropXPath['quesCont'], 'innerText', quesObj, 'quesCont', 0)
	print('获取问题内容...')
	if quesObj['quesType'].find('选择题') >= 0:
		parseQues(driver, mapPropXPath['opts'], 'innerText', quesObj, 'opts', 0)
		print('获取问题选项...')
		while driver.window_handles.__len__() < 2:
			driver.execute_script("ViewAnswers('//api.ppkao.com/mnkc/tiku/?id=" + str(i) + "','432')")
			time.sleep(5)
		doSwitchPage(driver)
		print('页面切换到答案页面...')
		closeOtherPages(driver)
		print('关闭其他页面...')
		parseQues(driver, mapPropXPath['ansImgBase64'], 'src', quesObj, 'ansImgBase64', 0)
		print('获取答案图片BASE64编码...')
		quesObj['ansGrayBase64'] = getGrayBase64(quesObj['ansImgBase64'])
		print('灰度处理...')
		parseQues(driver, mapPropXPath['interpretation'], 'innerText', quesObj, 'interpretation', 1)
		print('获取诠释...')
	elif quesObj['quesType'].find('问答题') >= 0 or quesObj['quesType'].find('填空题') >= 0:
		parseQues(driver, mapPropXPath['ansTxt'], 'innerText', quesObj, 'opts', 0)
		quesObj['ansImgBase64'] = ''
		quesObj['interpretation'] = ''
	save(i, quesObj)
	print('问题' + str(i) + '已保存')
	#del quesObj
	time.sleep(5)
