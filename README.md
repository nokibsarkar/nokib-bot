# Scripts
Specific task for the bot named <code>নকীব বট</code> in Bengali Wikipedia. It includes:
* <code>ga.py</code>: The script for maintaining Good Articles in Bengali Wikipedia.
* <code>cat.py</code>: The script for maintaining redirected categories.
* <code>reduceImage.py</code>: The script for reducing Overly pixeled non-free image.
* <code><del>editWar.py</del> <ins>realtime.py</ins></code>: The script for maintaining realtime tasks.
* <code>schedule.cron</code>: The cron file which controls the periodical activity of the tasks.
# Admin Scripts
* <code>delete_nonfree.py</code>: The script for deleting non-reduced version of non-free images. The script has will skip the file if:
**... the file is a SVG (There are some issues regarding these)
**... the last upload date did not pass a week
**... the file does not have the template {{মুক্ত নয় হ্রাসকৃত}} transcluded
In order to run this file,
* Check you have install <code>Pywikibot</code> library properly.
* Save the two files <code>setup.py</code> and <code>delete_nonfree.py</code> in your working directory.

