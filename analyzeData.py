import cv2
import numpy as np
import glob
import os

def estimateGamma(grayImg):
    # Estimate gamma from average luminance
    L = grayImg.astype(np.float32) / 255.0
    L = np.clip(L, 1e-6, 1.0)
    Lmean = np.mean(L)
    gamma = np.log(0.5) / np.log(Lmean)
    return gamma

def analyzeFrames(frameFolder):
    # Find all frames in folder
    framePaths = sorted(glob.glob(os.path.join(frameFolder, "*.jpg")))
    if not framePaths:
        print("No frames found!")
        return None

    rVals = []
    bVals = []
    sVals = []
    gammaVals = []

    print(f"Found {len(framePaths)} frames. Beginning analysis...")

    for path in framePaths:
        frame = cv2.imread(path)
        if frame is None:
            continue

        # Gray World white balance
        bMean = np.mean(frame[:,:,0])
        gMean = np.mean(frame[:,:,1])
        rMean = np.mean(frame[:,:,2])

        avg = (rMean + gMean + bMean) / 3

        if avg < 1:
            continue

        rVals.append(rMean / avg)
        bVals.append(bMean / avg)

        # Saturation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        sVals.append(np.mean(hsv[:,:,1]))

        # Gamma estimate
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gammaVals.append(estimateGamma(gray))

    # Return final dictionary
    return {
        "avgRoverGray": float(np.mean(rVals)),
        "avgBoverGray": float(np.mean(bVals)),
        "meanSaturation": float(np.mean(sVals)),
        "estimatedGamma": float(np.mean(gammaVals)),
    }

if __name__ == "__main__":
    ITML = r"frameITMFL"
    FA = r"frameFA"
    # stats = analyzeFrames(ITML)
    # stats = analyzeFrames(FA)
    def stylizeImage(inputImg, movieStats):

    print("\n=== FINAL RESULTS ===")
    print(stats)
