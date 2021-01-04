# IcebergShipDetection

## To be done
- Training of model
    - [x] Test different filters for initital image denoising. - see CNN_test_different_speckle_filters.ipynb on CNN_Trial_and_Error branch. **Results:** Not much difference in training results, but bilateral filter and Lee appear to denoise best. Bilateral is quite slow, so use **&rarr; Lee filter** 
    - [x] split data for training, validation and tesing (7-2-1) and implement testing - see CNN_training_iceberg_ship.ipynb on main branch
    - [x] test different optimizers - see CNN_test_different_optimizers.ipynb on CNN_Trial_and_Error branch. **Results:** Curves of the loss of SGD+Nesterov and RMSprop is quite jaggy. Adam learns fast in the beginning but shows overfitting after approx. 250 to 300 epochs. SGD needs more epochs to get nice results, but it curves look the best after 500 epochs. Test accuracy: Adam: 0.83, SGD: 0.87, SGD+Nesterov: 0.89, RMSprop: 0.86. **Use either SGD or Adam with higher dropouts to prevent overfitting**
    - [ ] test different 3rd bands (HH-HV, ratios, etc.)
    - [ ] review model architecture
    - [ ] choose a model ;)

- Object detection
    - [ ] Add class labels, probabilities of prediction and legend to the last plot.
    - [ ] Plot some "real" (projected) maps with (e.g. with cartopy) or produce at least tables containing the coordinates of the objects
    - [ ] Check how the model performs with our testscenes
    
- Testing with real-life data
    - [ ] Get recent position data of Polarstern or other vessels
    - [ ] Find test scenes, process them and check for plausibility
    - [ ] Check how the model performs if the extracted 75x75 subset contains multiple objects. I don't know how often this will happen in real life, but the model has not been trained to such images...

- Peer review in next seminar (January 5th): 
    - [x] Prepare short descriptions for the project
        - Topic of the project: Iceberg and ship detection in satellite imagery
        - Details of the project: The dataset in our project is obtained from Kaggle challenge, [Statoil/C-CORE Iceberg Classifier](https://www.kaggle.com/c/statoil-iceberg-classifier-challenge), each image has 75x75 pixels with two bands from HH and HV polarisations at certain incident angle. 
         - Goals of the project: The project plans to reach the goal of detecting whether an image contains a ship or an iceberg in Sentinel-1 SAR imagery, which is pre-processed with Sentinel Application Platform (SNAP) Python API ourselves.

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
