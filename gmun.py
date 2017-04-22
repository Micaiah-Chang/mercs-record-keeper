host = "https://www.gamefaqs.com/"

BOT_NAME = "mercscrawler"
# User-Agent data, to identify my crawler to GameFAQs
agent = 'Mozilla/5.0 (compatible; %s/1.0;)' % BOT_NAME
# these are just cookies to log into the GameFAQs account LogFAQs, so I can read at 50 tpp/ppp
cookies = 'dfpsess=###########; fv20170404=1; geo2=###########; ctk=###########; MDAUAuth=###########'
# robot parser ensures this crawler follows the guidelines of GameFAQs's robots.txt rules.
rp = robotparser.RobotFileParser()
rp.set_url(host + "robots.txt")
rp.read()
bname = "Board 8"
blink = "8-gamefaqs-contests"
url = host + "boards/" + blink + "/" + str(tid) + "?page=" + str(cpage-1)
# checks * crawler permissions
permission = rp.can_fetch("*", url)
# checks for rules specific to this crawler
permission &= rp.can_fetch(BOT_NAME, url)
# if allowed to read this page...
if permission:
	req = urllib2.Request(url)
	req.add_header('User-Agent', agent)
	req.add_header('Cookie', cookies)
	resp = urllib2.urlopen(req)
	page = resp.read()
	try:
		numpages = int(page[page.index('<li>Page'):].split('of ')[1].split('</li>')[0])
	except ValueError:
		numpages = 1
	# posttable = contents of the page between <table> and </table> tags, since only exists one.
	try:
		posttable = page[page.index('<table class="board'):].split('</table>')[0] + "</table>"
	except ValueError:
		print("Error reading table")
		sys.exit()
	postsplit = posttable.split('</tr>')
	# postsplit gets each row from the <table>, essentially outputting an array of posts to cycle through...
	print(bname+" -> " + str(tid))
	print("\tStart: Page " + str(cpage) + "/" + str(numpages))
	for item in postsplit:
		item = item + "</tr>"
		# skip deleted posts
		if "msg_deleted" in item:
			print("\tPost Deleted.")
			continue
		# final item will be after the last </tr>, which is just the </table> ending tags
		if "</table>" in item:
			print("\tEnd: Page " + str(cpage) + "/" + str(numpages))
			break
		# parsing out post author, pid, date, post message, and post number
		postAuthor = item[item.index('data-username="')+len('data-username="'):].split('"')[0]
		postID = item[item.index('data-msgid="')+len('data-msgid="'):].split('"')[0]
		dateInfo = item[item.index('"post_time" title="')+len('"post_time" title="'):].split('"')[0].replace('&nbsp;','')
		postDate = datetime.strptime(dateInfo, '%m/%d/%Y %I:%M:%S%p')
		postsrch = 'name="'+postID+'">'
		postMsg = item[item.index(postsrch)+len(postsrch):].split('</div><div class="msg')[0]
		postNum = item[item.index('">#')+len('">#'):].split('</a>')[0]
		# mysql feeds parsed data into my database
		try:
			cursor = conn.cursor()
		except mysql.connector.errors.OperationalError:
			conn.close()
			conn = mysql.connector.connect(**dbset)
			cursor = conn.cursor()
		add_post = ("[mysql insertion line]")
		post_data = ([values inserting into database])
		try:
			# performs the mysql command
			cursor.execute(add_post, post_data)
			print("\t" + postNum + ": Post ["+postID+"] By " + postAuthor + " at " + dateInfo + "... Inserted!")
		except mysql.connector.errors.IntegrityError:
			print("\t" + postNum + ": Post ["+postID+"] By " + postAuthor + " at " + dateInfo + "... Exists!")
		cursor.close()
	more = numpages > cpage
	# if topic contains more pages, runs the script again on the next page (cpage+1)
	if more:
		# out of courtesy waits 2 seconds between page reads so I don't annoy gamefaqs
		time.sleep(2)
		exnext = "~#########/subbot " + str(bid) + " " + str(tid) + " " + str(cpage+1)
		os.system(exnext)
	else:
		print
else:
	# else = crawler doesn't have permission to read this page
	print("Goodbye, World!")
