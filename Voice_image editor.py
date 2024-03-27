from image import Image
import numpy as np
import speech_recognition as sr
import os
import win32com.client 

speaker = win32com.client.Dispatch("SAPI.SPvoice")

def write(text):
    os.system(f"echo {text}")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language="en-in")
            print(f"user said: {query}")
            return query
        except Exception as e:
            return "some error occured"

def brighten(image, factor):
    # when we brighten, we just want to make each channel higher by some amount 
    # factor is a value > 0, how much you want to brighten the image by (< 1 = darken, > 1 = brighten)
    x_pixels, y_pixels, num_channels = image.array.shape  
    new_im = Image(x_pixels=x_pixels, y_pixels=y_pixels, num_channels=num_channels)  

    new_im.array = image.array * factor

    return new_im

def adjust_contrast(image, factor, mid):
    # adjust the contrast by increasing the difference from the user-defined midpoint by factor amount
    x_pixels, y_pixels, num_channels = image.array.shape  
    new_im = Image(x_pixels=x_pixels, y_pixels=y_pixels, num_channels=num_channels)  
    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
                new_im.array[x, y, c] = (image.array[x, y, c] - mid) * factor + mid

    return new_im

def blur(image, kernel_size):
    # kernel size is the number of pixels to take into account when applying the blur
    # (ie kernel_size = 3 would be neighbors to the left/right, top/bottom, and diagonals)
    # kernel size should always be an *odd* number
    x_pixels, y_pixels, num_channels = image.array.shape  # represents x, y pixels of image, # channels (R, G, B)
    new_im = Image(x_pixels=x_pixels, y_pixels=y_pixels, num_channels=num_channels)  # making a new array to copy values to!
    neighbor_range = kernel_size // 2  # this is a variable that tells us how many neighbors we actually look at (ie for a kernel of 3, this value should be 1)
    
    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
                # we are going to use a naive implementation of iterating through each neighbor and summing
                # there are faster implementations where you can use memoization, but this is the most straightforward for a beginner to understand
                total = 0
                for x_i in range(max(0,x-neighbor_range), min(new_im.x_pixels-1, x+neighbor_range)+1):
                    for y_i in range(max(0,y-neighbor_range), min(new_im.y_pixels-1, y+neighbor_range)+1):
                        total += image.array[x_i, y_i, c]
                new_im.array[x, y, c] = total / (kernel_size ** 2)
    return new_im

def apply_kernel(image, kernel):
    # the kernel should be a 2D array that represents the kernel we'll use!
    # for the sake of simiplicity of this implementation, let's assume that the kernel is SQUARE
    # for example the sobel x kernel (detecting horizontal edges) is as follows:
    # [1 0 -1]
    # [2 0 -2]
    # [1 0 -1]
    x_pixels, y_pixels, num_channels = image.array.shape  # represents x, y pixels of image, # channels (R, G, B)
    new_im = Image(x_pixels=x_pixels, y_pixels=y_pixels, num_channels=num_channels)  # making a new array to copy values to!
    neighbor_range = kernel.shape[0] // 2  # this is a variable that tells us how many neighbors we actually look at (ie for a 3x3 kernel, this value should be 1)
    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
                total = 0
                for x_i in range(max(0,x-neighbor_range), min(new_im.x_pixels-1, x+neighbor_range)+1):
                    for y_i in range(max(0,y-neighbor_range), min(new_im.y_pixels-1, y+neighbor_range)+1):
                        x_k = x_i + neighbor_range - x
                        y_k = y_i + neighbor_range - y
                        kernel_val = kernel[x_k, y_k]
                        total += image.array[x_i, y_i, c] * kernel_val
                new_im.array[x, y, c] = total
    return new_im

def combine_images(image1, image2):
    # let's combine two images using the squared sum of squares: value = sqrt(value_1**2, value_2**2)
    # size of image1 and image2 MUST be the same
    x_pixels, y_pixels, num_channels = image1.array.shape  # represents x, y pixels of image, # channels (R, G, B)
    new_im = Image(x_pixels=x_pixels, y_pixels=y_pixels, num_channels=num_channels)  # making a new array to copy values to!
    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
                new_im.array[x, y, c] = (image1.array[x, y, c]**2 + image2.array[x, y, c]**2)**0.5
    return new_im
    




if __name__== '__main__':
    lake = Image(filename='lake.png')
    city = Image(filename='city.png')


    write("hello, I'm your personal image editor assistant")
    while True:
        print("listening.....")
        query = take_command()
        speaker.Speak(query)

        if "who are you" in query.lower():
            write("I'm your personal AI assistant, I'll help you in editing your photos.")
            speaker.speak("I'm your personal AI assistant, I'll help you in editing your photos.")
        
        # To open the original image
        images = [["lake", r"C:\vitual codes\codes\venv\input_files\lake.png", lake],["city", r"C:\vitual codes\codes\venv\input_files\city.png",city]]
        for image in images:

            if f"open {image[0]} image".lower() in query.lower():
                write(f"opening {image[0]}")
                os.startfile(image[1])

            output_brightness_file = f"{image[0]}_brightened.png"
            output_contrast_file = f"{image[0]}_contrast.png"
            output_blur_file = f"{image[0]}_blur.png"
            X_axis_edge_output = f"{image[0]}_edge_x.png"
            Y_axis_edge_output = f"{image[0]}_edge_y.png"
            XY_axis_edge_output = f"{image[0]}_edge_xy.png"


        # To increase the brightness
        if f"increase brightness of image {image[0]}" in query.lower() or f"decrease brightness of image {image[0]}" in query.lower():
            factor_brightness = float(input("pagal enter the factor,increase(>1) or decrease(<1): "))
            brightened_adjust = brighten(image[2], factor_brightness)
            output_brightness_file = f"{image[0]}_brightened.png"
            brightened_adjust.write_image(output_brightness_file)

        if f"increase contrast of image {image[0]}" in query.lower() or f"decrease contrast of image {image[0]}" in query.lower():
            factor_contrast = float(input("enter the factor,increase(>1) or decrease(<1): "))
            mid_contrast = float(input("enter the mid: "))
            output_contrast_file = f"{image[0]}_contrast.png"
            contrast_adjust = adjust_contrast(image[2], factor_contrast, mid_contrast)
            contrast_adjust.write_image(output_contrast_file)

        if f"blur my image {image[0]}" in query.lower():
            size = float(input("enter the kernel size, i.e to much you want to blur the image"))
            output_blur_file = f"{image[0]}_blur.png"
            blur_adjust = blur(image[2], size)
            blur_adjust.write_image(output_blur_file)


        if f"show the X axis edge of image {image[0]}" in query.lower():
            sobel_x = apply_kernel(image[2], np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]))
            X_axis_edge_output = f"{image[0]}_edge_x.png"
            sobel_x.write_image(f"{image[0]}_edge_x.png")


        if f"show the Y axis edge of image {image[0]}" in query.lower():
            sobel_y = apply_kernel(image[2], np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]]))
            Y_axis_edge_output = f"{image[0]}_edge_y.png"
            sobel_y.write_image(f"{image[0]}_edge_y.png")

        if f"show the X and Y axis edge of image {image[0]}" in query.lower():
            sobel_xy = combine_images(sobel_x, sobel_y)
            XY_axis_edge_output = f"{image[0]}_edge_xy.png"
            sobel_xy.write_image(f"{image[0]}_edge_xy.png")


        modified_image = [["brightned", output_brightness_file],["contrast", output_contrast_file],["blur", output_blur_file],\
                            ["x edge",X_axis_edge_output],["y axis", Y_axis_edge_output],["x and y axis", XY_axis_edge_output]]
        output_image_path = "C:\\vitual codes\\codes\\venv\\output_files"
        for mod_img in modified_image:
            if f"open modified {mod_img[0]} image" in query.lower():
                modified_file_path = os.path.join(output_image_path, mod_img[1])
                print(modified_file_path)
                os.startfile(modified_file_path)

                



            
                
                

            
