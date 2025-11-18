import random
from pornhub_api import PornhubApi

api = PornhubApi()

#tags = "Blonde"
#tags = random.sample(api.video.tags("f").tags, 5)
tags = api.video.tags("f").tags
#category = "Babe"
#category = random.choice(api.video.categories().categories)
category = api.video.categories().categories
result = api.search.search_videos(ordering="Featured Recently", tags=tags, category=category)

print(result.size())
for vid in result:
    print(vid.title, vid.url)

#print(tags)
#print(category)

#for tag in tags:
#    print(tag)

#for cat in category:
#    print(cat)

#print(api.stars.all())
