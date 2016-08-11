def log_insertion(string):
	path = xbmc.translatePath(os.path.join('special://home/addons',ADDON))
	file_ = path + ADDON + '.log'
	with open("test.txt", "a") as myfile:
    myfile.write("string")