# Include the Dropbox SDK
import os, dropbox

class Dropbox:
    def __init__(self, path):
        self.path = path
        access_token = '###########################'
        self.client = dropbox.client.DropboxClient(access_token)

    def downloadMusic(self):
        path = self.path + "/Music/"
        # Delete current playlist
        os.system("rm -R " + path)

        # Create and download new one
        os.system("mkdir " + path)

        # List Dropbox folder
        metadata = self.client.metadata('/Music/')

        for file in metadata["contents"]:
            dropboxPath = file["path"]
            nameFile = file["path"].split("/")[-1:][0]

            f, metadata = self.client.get_file_and_metadata(dropboxPath)
            out = open(path + nameFile, 'wb')
            out.write(f.read())
            out.close()
            print nameFile

        return "All music downloaded"

    def uploadIMG(self):
        path = self.path + "/DCIM/"
        if os.listdir(path):
            for file in os.listdir(path):
                print file
                f = open(path + file, 'rb')
                self.client.put_file("/DCIM/" + file, f)
                os.remove(path + file)
                print file + "uploaded successfuly"
            return "All photos uploaded to dropbox"
        else: 
            return "No photos to be uploaded"
        
if __name__ == '__main__':
    path = os.getcwd()
    dropbox = Dropbox("/".join(path.split("/")[0:-1]))
    print dropbox.uploadIMG()
    print dropbox.downloadMusic()