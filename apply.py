import cv2
import numpy as np
import analyzeData
import glob

# white balance
def applyWhiteBalance(img, rRatio, bRatio):
    imgF = img.astype(np.float32)
    imgF[:,:,2] *= rRatio
    imgF[:,:,0] *= bRatio
    return np.clip(imgF, 0, 255).astype(np.uint8)

# saturation adjust
def applySaturation(img, targetSat, currentSat):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1] *= (targetSat / (currentSat + 1e-6))
    hsv = np.clip(hsv, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

# gamma correction
def applyGamma(img, gamma):
    imgF = img.astype(np.float32) / 255.0
    out = np.power(imgF, 1.0/gamma)
    return np.clip(out * 255, 0, 255).astype(np.uint8)

# three-way color grading
def applyThreeWayColor(img, shadowColor, midColor, highlightColor,
                       shadowStrength=0.4, midStrength=0.4, highlightStrength=0.4):

    imgF = img.astype(np.float32) / 255.0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    shadowMask = np.clip(1.0 - gray*2.0, 0, 1)
    midMask = 1.0 - np.abs(gray - 0.5)*2.0
    highlightMask = np.clip((gray*2.0) - 1.0, 0, 1)

    shadowMask = shadowMask[:,:,None]
    midMask = midMask[:,:,None]
    highlightMask = highlightMask[:,:,None]

    out = imgF.copy()
    out += shadowStrength * shadowMask * (shadowColor / 255.0)
    out += midStrength * midMask * (midColor / 255.0)
    out += highlightStrength * highlightMask * (highlightColor / 255.0)

    return np.clip(out * 255, 0, 255).astype(np.uint8)

# per-channel S curve
def applyChannelCurves(img, rPow, gPow, bPow):
    imgF = img.astype(np.float32) / 255.0
    B = imgF[:,:,0]
    G = imgF[:,:,1]
    R = imgF[:,:,2]

    def s_curve(x, p):
        x = np.clip(x, 0, 1)
        return (x**p) / (x**p + (1-x)**p + 1e-6)

    R2 = s_curve(R, rPow)
    G2 = s_curve(G, gPow)
    B2 = s_curve(B, bPow)

    out = np.stack([B2, G2, R2], axis=2)
    return np.clip(out * 255, 0, 255).astype(np.uint8)

# full stylization
def stylizeImage(inputImg, movieStats):
    rRatio = movieStats["avgRoverGray"]
    bRatio = movieStats["avgBoverGray"]
    targetSat = movieStats["meanSaturation"]
    gamma = movieStats["estimatedGamma"]

    out = applyWhiteBalance(inputImg, rRatio, bRatio)

    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV)
    currentSat = np.mean(hsv[:,:,1])
    out = applySaturation(out, targetSat, currentSat)

    shadowTint = np.array([40, 120, 20])
    midTint = np.array([120, 20, 120])
    highlightTint = np.array([40, 200, 200])
    out = applyThreeWayColor(out, shadowTint, midTint, highlightTint)

    out = applyChannelCurves(out, rPow=1.2, gPow=1.0, bPow=1.4)

    out = applyGamma(out, gamma)

    return out

# main block
if __name__ == "__main__":
    folder = r"frameFA"
    faStats = analyzeData.analyzeFrames(r"frameFA")
    mLStats = analyzeData.analyzeFrames(r"frameITMFL")
    # input_path = r"testInputs/arcade.jpg"
    # inputIm = cv2.imread(input_path)

    # if inputIm is None:
    #     raise FileNotFoundError("Image not found at: " + input_path)

    # styled = stylizeImage(inputIm, stats)
    # cv2.imwrite("example.jpg", styled)

    inFolder = r"testInputs"
    count = 1
    for fp in glob.glob(inFolder + "/*"):
        inputIm = cv2.imread(fp)

        styledFA = stylizeImage(inputIm, faStats)
        cv2.imwrite(f"photo{count}FA.jpg", styledFA)

        styledML = stylizeImage(inputIm, mLStats)
        cv2.imwrite(f"photo{count}ML.jpg", styledML)
        count += 1

    print("Saved styled image as example.jpg")
