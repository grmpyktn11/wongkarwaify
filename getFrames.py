import cv2
import os
import os.path

def extractFrames(videoPath, interval=60):

    #output folder

    videoFileName = os.path.basename(videoPath)

    movieName = os.path.splitext(videoFileName)[0]

    outputFolder = f"frame{movieName}"
    os.makedirs(outputFolder, exist_ok=True)

    print(f"Output folder: {outputFolder}")

    #open video file
    cap = cv2.VideoCapture(videoPath)

    if not cap.isOpened():
        print('couldnt open video')
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"fps:{fps}")
    print(f"total frame amt = {totalFrames}")

    #claculate how many frames to skip each sample
    #example: if fps=30 and intseconds = 2 then frame interval is 60
    frameInterval = int(fps * interval)

    print(f"taking 1 frame every {interval} seconds. the interval is {frameInterval} apart")

    frameID = 0 #where in video we jump to
    savedID = 0 #how many frames we saved

    #loop to extract frame
    while True:
        #move to desired frame number in vid
        cap.set(cv2.CAP_PROP_POS_FRAMES, frameID)

        #read frame at this pos
        ret, frame = cap.read()

        #if video done end
        if not ret:
            break

        #build filename
        filename = os.path.join(outputFolder, f"frame{savedID:05}.jpg")

        #save the frame img
        cv2.imwrite(filename, frame)

        savedID += 1
        frameID += frameInterval

    #cleanup
    cap.release()

    print(f"done!!")    

if __name__ == '__main__':
    extractFrames(r"C:\Users\ih841\OneDrive\Documents\GitHub\wongkarwaify\FA.mp4")