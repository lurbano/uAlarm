import os 

# path = "/home/lurbano/Music/"
# dir_list = os.listdir(path)
# print(sorted(dir_list, key=str.lower))

def getAllArtists():
    path = "/home/lurbano/Music/"
    dir_list = os.listdir(path)
    return sorted(dir_list, key=str.lower)

print(getAllArtists())

def getAllSongs(artist=None):
    if artist == None:
        return None
    else:
        path = f"/home/lurbano/Music/{artist}"
        dir_list = os.listdir(path)
        return dir_list
    
songs = getAllSongs("Linkin Park")
print(songs)
