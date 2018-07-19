# This file contains a simplified demonstration of the techniques discussed in the How We React paper. 
# Though the techniques used herein are decidedly rudimentary, they are meant to serve as a litmus test
# for the efficacy of these new means of polling and as a testament to the robustness of politically-focused
# subreddits as a dataset.

# Creates Reddit instance using PRAW reddit api wrapper for Python
def getInstance():
	import praw
	import sys
	reddit = praw.Reddit(client_id='ypKZSjFC8JGvFA',
                     client_secret='THDdmFN9ZL3FYaTTJzNKVCIDH-E',
                     user_agent='example user_agent',
                     username='example user name',
                     password='example password')

	return (reddit)

# Scrapes comments of AP article from r/donald source, using top as a means to avoid some inherent issues with
# PRAWS direct-to-url calls for articles
def scrapeDonald():
	file = open('exportFile_donald.txt','w') 
	reddit = getInstance()
	subreddit = reddit.subreddit('The_Donald')
	for submission in subreddit.top(limit=1):
		submission.comments.replace_more()
		comments = submission.comments
		for top_level_comment in submission.comments:
			file.write('\n-----------------------------------')
			file.write('\n')
			file.write(top_level_comment.body.encode('ascii', 'ignore'))
			file.write('\n')
			file.write('\n-----------------------------------')

	file.close()
	print ('done')

# Scrapes comments of AP article from r/news (left-leaning) source
def scrapeNews():
	file = open('exportFile_news.txt', 'w')
	reddit = getInstance()
	submission = reddit.submission(url='https://www.reddit.com/r/news/comments/5bzjbe/donald_trump_elected_president/')
	submission.comments.replace_more()
	comments = submission.comments
	for top_level_comment in submission.comments:
		file.write('\n-----------------------------------')
		file.write('\n')
		file.write(top_level_comment.body.encode('ascii', 'ignore'))
		file.write('\n')
		file.write('\n-----------------------------------')
	file.close()
	print ('done')

# Accessing 'filter' for common words. Incredibly rudimentary, but necessar
def getFilter():
	ret = []
	filter_file = open('commonWords.txt', 'r')
	filter_words = filter_file.read().split(',')
	for word in filter_words:
		ret.append(word)

	return ret


# carries out issue sentiment analysis and issue BOW as discussed in paper
def processTextFile(file_name):
	print ('PROCESSING FILE FOR: ', file_name)
	import collections
	import nltk
	from textblob import TextBlob
	sno = nltk.stem.SnowballStemmer('english')  # making (relatively safe assumption) that most comments of interest
												# are in english
	my_filter = getFilter()
	text_file = open(file_name, 'r')

	comments = []
	word_counts = {}
	lines = text_file.read().split('-----------------------------------')
	words_filtered_count = 0

	# issue for sentiment target analysis
	sentiment_issue= "canada"

	# issue for bag of words analysis
	bow_issue = "establishment"

	
	issue_sentiment_sum = 0
	issue_sentiment_tag_count = 0

	issue_bow = {}

	for line in lines:
		comments.append(line)
	for i in range(0, len(comments)):
		comment = comments[i]
		blob = TextBlob(comment)

		# issue-targetted sentiment analysis scores
		if (sentiment_issue.lower() in blob.lower()):
			# if comment includes issue

			# if sentiment analysis registers
			if (not (blob.sentiment.polarity == 0.0)):
				issue_sentiment_sum += blob.sentiment.polarity
				issue_sentiment_tag_count += 1

		# issue-targetted bag of words
		if (bow_issue.lower() in blob.lower()):

			# if comment includes issue
			for associated_term in blob.lower().split():

				if ((not associated_term in my_filter) and (not associated_term == bow_issue.lower())):

					associated_term = sno.stem(associated_term)

					if (not associated_term in issue_bow.keys()):
						issue_bow[associated_term] = 0
					else:
						issue_bow[associated_term] += 1


	total_comment_count = len(comments)
	issue_sentiment_score = (1.0 * issue_sentiment_sum) / (issue_sentiment_tag_count)

	print ('here is bag of words for issue: ' + bow_issue)
	sort_bow = collections.OrderedDict(sorted(issue_bow.items(), key=lambda t: t[1]))
	for k, v in sort_bow.iteritems():
		if v > 1:
			print (str(k) + ": " + str(v))

	print ('\n')
	print ('total_comment_count', total_comment_count)
	print ('issue_sentiment_score for issue: ' + sentiment_issue+ ' is: ' + str(issue_sentiment_score))


def main():
	already_scraped = False
	if (not already_scraped):
		scrapeDonald()
		scrapeNews()
	else:
		processTextFile('exportFile_donald.txt')
		processTextFile('exportFile_news.txt')

if __name__ == '__main__':
	main()
