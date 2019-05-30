from app.api.coverpy_api import coverpy


def get_cover_img_url(track_name):
    # print(track_name)
    c = coverpy.CoverPy()
    query = c.get_cover(str(track_name))
    # print("Name: %s" % query.name)
    # print("EntityType: %s" % query.type)
    # print("Artist: %s" % query.artist)
    # print("Album: %s" % query.album)
    try:
        url = str(query.artwork())
    except:
        url = "NONE"
    # print("QueryUrl: %s" % query.url)
    return url

# print(get_cover_img_url("Love Someone"))
