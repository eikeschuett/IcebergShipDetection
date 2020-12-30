# IcebergShipDetection

## To be done
- Training of model
    - split data for training, testing and validation (7-2-1)
    - implement validation
    - choose a model ;)

- Object detection
    - Check how the model performs with our testscenes
        - Check how the model performs if the extracted 75x75 subset contains multiple objects. I don't know how often this will happen in real life, but the model has not been trained to such images...
    - Add class labels, probabilities of prediction and legend to the last plot.
    - Plot some real (projected) maps with (e.g. with cartopy)
    
- Find test scenes, process them and check for plausibility
    - Ask for recent position data of Polarstern

- Prepare for review during next seminar (What do we have to do/present exactly?)

## Links

### Preprocessing with Snappy
**[Some code on Github](https://github.com/wajuqi/Sentinel-1-preprocessing-using-Snappy)**
**[ESA Webinar](https://www.youtube.com/watch?v=PiU68g3WRIY)**

### Object Detection and Models
**[Short article and code of another solution for the kaggle contest on towardsdatascience.com](https://towardsdatascience.com/deep-learning-for-iceberg-detection-in-satellite-images-c667acf4bad0)**

**[Paper on this topic (Heiselberg 2020)](https://www.mdpi.com/776368)**

**[Almost the same paper (?), but in a differnet journal](https://www.researchgate.net/publication/342681947_Ship-Iceberg_Detection_and_Classification_in_Sentinel-1_SAR_Images)**

**[Ship detection in Sentinel-2 RGBs](https://medium.com/the-downlinq/object-detection-in-satellite-imagery-a-low-overhead-approach-part-i-cbd96154a1b7)**



## **[Requirements for the project](https://opencampus.gitbook.io/opencampus-machine-learning-program/projects/requirements)**:

- Presentation of a detailed Jupyter Notebook with code and comment
    - including the definition of the environment
    - including required sections (Introduction, Data and Methods, Results, Baseline)
- A small video, accompanying, for example, a screen recording of the notebook with an explanation of the challenge of the project, the used approach, and the results.
- A statement that the code is released as open source software. The data you use in your project can remain private if you wish.
