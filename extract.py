import os
import numpy as np
import argparse
from PIL import Image

class ImageExtractorInChunks(object):
    def __init__(self, image_path, thumb_save_path, thumbnail_size=1072, chunk_size=[352,592], stride=[240,480]):
        
        self.image_path = image_path
        self.save_path = thumb_save_path
        self.thumbnail_size = thumbnail_size
        self.chunk_size = chunk_size
        self.stride = stride
        self.thumb_images = []

        for root, dirs, files in os.walk(self.image_path):
            if not os.path.exists(os.path.join(self.save_path, root)):
                save_ = os.path.join(self.save_path, root)
                os.makedirs( save_)

            for file in files:
                path = os.path.join(root, file)
                image = Image.open(path).convert('RGB')
                image.thumbnail((self.thumbnail_size, self.thumbnail_size))
                img_array = np.array(image)
                image.save(f"{save_}/{file}")
                self.thumb_images.append({"image": img_array, "path":  save_, "filename": file})

    def add_x_axis(self, img, value=-1):
        new = img[:,:value,:]
        added = np.append(img, new, axis=1)
        
        return added

    def add_y_axis(self, img, value=-1):
        new = img[:value,:,:]
        added = np.append(img, new, axis=0)

        return added

    def padding(self, object):
        for i in object:
            img = i["image"]
            filename = i["filename"]
            path = i["path"]

            self.padded_img_path = os.path.join("padded_images", path)
            if not os.path.exists(self.padded_img_path):
                os.makedirs(self.padded_img_path)

            image = np.array(img)
            if image.shape[1] < image.shape[0]:
                while image.shape[1] < image.shape[0]:
                    value = image.shape[0] - image.shape[1]
                    if value < image.shape[1]:
                        image = self.add_x_axis(image, value)
                    else:
                        image = self.add_x_axis(image)
                    padded_image  = Image.fromarray(image)

            elif image.shape[0] < image.shape[1]: 
                while image.shape[0] < image.shape[1]:
                    value = image.shape[1] - image.shape[0]
                    if value < image.shape[0]:
                        image = self.add_y_axis(image, value)
                    else:
                        image = self.add_y_axis(image)

                    padded_image = Image.fromarray(image)

            else:
                padded_image = Image.fromarray(image)

            padded_image.save(f"{self.padded_img_path}/{filename}")

    def create_chunks(self, padded_img_path, scale=[1,2]):
        chunks = []

        for root, dirs, files in os.walk(padded_img_path):
            save_chunk_path = os.path.join("chunk_images", root)
            if not os.path.exists(save_chunk_path):
                os.makedirs(save_chunk_path)

            for file in files:
                count = 0
                path = os.path.join(root, file)
                image = Image.open(path).convert('RGB')
                img_array = np.array(image)
            
                for i, chunkSize in  enumerate(self.chunk_size):
                    for x in range(0, self.thumbnail_size , self.stride[i]):
                        for y in range(0, self.thumbnail_size , self.stride[i]):
                            chunk = img_array[x : x+chunkSize, y: y+chunkSize]
                            if chunk.shape[0] == chunkSize and chunk.shape[1] == chunkSize:
                                chunk = Image.fromarray(chunk)
                                chunk.save(f"{save_chunk_path}/{count}_{chunkSize}_{file}")
                                count += 1

def main():
    args = argparse.ArgumentParser()
    args.add_argument("--image_path", type=str, required=True, help="path to source images")
    args.add_argument("--thumb_save_path", type=str, required=True ,help="thumbnail_images save path")
    args.add_argument("--padding", action='store_true' ,  help="if use this flag, padding will be applied")
    args.add_argument("--create_chunks", action='store_true',  help="if use this flag, chunks will be created")
    args.add_argument("--thumbnail_size", type=int, default=1072)
    args.add_argument("--chunk_size", type=int, nargs="+", default=[352,592])
    args.add_argument("--stride", type=int, nargs="+", default=[240,480])
    args = args.parse_args()

    image_extractor = ImageExtractorInChunks(args.image_path, args.thumb_save_path, args.thumbnail_size, args.chunk_size, args.stride)
    if args.padding is True:
        image_extractor.padding(image_extractor.thumb_images)

    if args.create_chunks is True:
        image_extractor.create_chunks("padded_images")

if __name__ == '__main__':
    main()