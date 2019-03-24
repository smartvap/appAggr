# AndEdu Exam Helper
# Remove restrictions of cutting screen, text copying & pasting and context menu
var remRestricts = function () {
	window.onblur = null
	document.getElementsByClassName("preview-content")[0].oncopy = "return true;"
	document.getElementsByClassName("achievement-content")[0].oncopy = "return true;"
	document.getElementsByClassName("preview-content")[0].onpaste = "return true;"
	document.getElementsByClassName("achievement-content")[0].onpaste = "return true;"
	document.getElementsByClassName("preview-content")[0].oncontextmenu = "window.event.returnValue = true;"
}

# Remove restrictions of exam time
var extExamTime = function () {
	
}