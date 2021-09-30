# How the app works : 

It can simulataneously serve multiple indexes


All indexes are stored on redis


When a new index is added, a flag is set


Indexes are immutable - once set they cannot be updated
However, their version can be bumped up - so that all previous version data can be added along with a new set of data

Data once added cannot be removed - the only way is to delete an entire set of indexes and start fresh

# After app starts

Add index api called with data


# How to Update the Chit-Chat Dataset Based on the Q&As Contained in the Script Given by Product Designers
Update the file called **Script-updated-database.xlsx** in the directory **production_data** with the new script, and push the code changes to GitHub and trigger a new build.
