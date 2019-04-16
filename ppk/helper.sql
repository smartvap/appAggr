-- Choose the tablespace
SELECT d.tablespace_name,
       SPACE"SUM_SPACE(M)",
       blocks sum_blocks,
       space - nvl(free_space, 0) "USED_SPACE(M)",
       round((1 - nvl(free_space, 0) / space) * 100, 2) "USED_RATE(%)",
       free_space "FREE_SPACE(M)"
  FROM (SELECT tablespace_name,
               round(SUM(bytes) / (1024 * 1024), 2) space,
               SUM(blocks) blocks
          FROM dba_data_files
         GROUP BY tablespace_name) d,
       (SELECT tablespace_name,
               round(SUM(bytes) / (1024 * 1024), 2) free_space
          FROM dba_free_space
         GROUP BY tablespace_name) f
 WHERE d.tablespace_name = f.tablespace_name(+)
 ORDER BY "FREE_SPACE(M)" DESC;

-- ppk ques table
CREATE TABLE t_ques
(
  sn_lnk     NUMBER(16) NOT NULL,
  ques_bank  VARCHAR2(512) NOT NULL,
  ques_type  VARCHAR2(512) NOT NULL,
  ques_cont  VARCHAR2(4000) NOT NULL,
  opts       VARCHAR2(4000),
  ans_img_c  CLOB,
  interpret  CLOB
)
TABLESPACE D_LOG_05
  PCTFREE 10
  INITRANS 1
  MAXTRANS 255
  STORAGE
  (
    INITIAL 2
    NEXT 2
    MINEXTENTS 1
    MAXEXTENTS UNLIMITED
    PCTINCREASE 0
  );
