import random
from pornhub_api import PornhubApi

api = PornhubApi()

#tags = "Blonde"
#tags = random.sample(api.video.tags("f").tags, 5)
category = "Babe", "Blonde"
#category = random.choice(api.video.categories().categories)
result = api.search.search_videos(ordering="Featured Recently", category=category)
#result = api.search.search_videos(ordering="Most Viewed", category=category)


print(result.size())
for vid in result:
    print(vid.title, vid.url)
