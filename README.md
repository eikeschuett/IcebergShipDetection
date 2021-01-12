# IcebergShipDetection

## To be done
- Training of model
    - [x] Test different filters for initital image denoising. - see CNN_test_different_speckle_filters.ipynb on CNN_Trial_and_Error branch. **Results:** Not much difference in training results, but bilateral filter and Lee appear to denoise best. Bilateral is quite slow, so use **&rarr; Lee filter** 
    - [x] split data for training, validation and tesing (7-2-1) and implement testing - see CNN_training_iceberg_ship.ipynb on main branch
    - [x] test different optimizers - see CNN_test_different_optimizers.ipynb on CNN_Trial_and_Error branch. **Results:** Curves of the loss of SGD+Nesterov and RMSprop is quite jaggy. Adam learns fast in the beginning but shows overfitting after approx. 250 to 300 epochs. SGD needs more epochs to get nice results, but it curves look the best after 500 epochs. Test accuracy: Adam: 0.83, SGD: 0.87, SGD+Nesterov: 0.89, RMSprop: 0.86. Experiences with other models show that Adam is more stable than SGD, esp. when including the inclination angle **Use Adam and pay attention to potential overfitting**
    - [x] test different 3rd bands (HH+HV, ratios, etc.). - see CNN_test_different_3rd_bands.ipynb. I tested HH+HV, HH-HV, HH*HV, HH/HV, HV-HH, HV/HH. **Results:** Most promising combinations are simple HH+HV and HH/HV. HH/HV has a higher accuracy (acc=0.891, val_acc=0.885) than HH+HV (acc=0.847, val_acc=0.85), but its loss curve is not as smooth as the HH+HV combination. The HH/HV loss curve also indicates some overfitting after around 200 epochs, which is not so pronounced in the HH+HV combination. Experiences after including the inclination angle also suggest that HH+HV is more stable and yields slightly higher accuracies. **Use HH+HV**
    - [ ] review model architecture
    - [ ] do the normalization of the inclination angle as a lambda layer in the model (because it looks fancy) and change normalization between 0 and 1 to get it to work with the RELU activation function
    - [ ] choose a model ;)

- Processing of S1-Scenes
    - [ ] Get .tif of localInclinationAngle during LandSeaMasking    

- Object detection
    - [ ] Import inclination angle, normalize it and feed it into the model
    - [ ] Add class labels, probabilities of prediction and legend to the last plot.
    - [ ] Plot some "real" (projected) maps with (e.g. with cartopy) or produce at least tables containing the coordinates of the objects
    - [ ] Check how the model performs with our testscenes
    
- Testing with real-life data
    - [ ] Get recent position data of Polarstern or other vessels
    - [ ] Find test scenes, process them and check for plausibility
    - [ ] Check how the model performs if the extracted 75x75 subset contains multiple objects. I don't know how often this will happen in real life, but the model has not been trained to such images...

- Peer review in next seminar (January 5th): 
    - [x] Prepare short descriptions for the project
        - Topic: Iceberg and ship detection in satellite imagery
         - Goals: The project goal is to build an algorithm for the detection of ships and icebergs in Sentinel-1 SAR imagery. Desired output is a map, which shows the locations of icebergs, ships and unidentified objects.
        - Details: The dataset used for training is obtained from a Kaggle challenge, [Statoil/C-CORE Iceberg Classifier](https://www.kaggle.com/c/statoil-iceberg-classifier-challenge). Each image has 75x75 pixels with two bands from HH and HV polarisations and contains a ship or an iceberg. This dataset will be used to train a CNN.
        After training the classification model, we will use Sentinel-1 SAR images to show the "real world application" of our model. The satellite images will be pre-processed with the Sentinel Application Platform (SNAP) Python API. We will then identify bright objects within each satellite image. A 75x75 subset of the radar image will be made for each object and fed into our classification model. Finally, the results will be plotted on a map.
        


## Links

### Preprocessing with Snappy
- **[Some code on Github](https://github.com/wajuqi/Sentinel-1-preprocessing-using-Snappy)**
- **[ESA Webinar](https://www.youtube.com/watch?v=PiU68g3WRIY)**
- [Suggesting processing workflow with SNAPPY on step forum](https://forum.step.esa.int/t/radiometric-geometric-correction-workflow/2540/35)

### Object Detection and Models
- **[Short article and code of another solution for the kaggle contest on towardsdatascience.com](https://towardsdatascience.com/deep-learning-for-iceberg-detection-in-satellite-images-c667acf4bad0)**
- **Ship-Iceberg Classification**
    - **[Using SAR and Multispectral Satellite Images with SVM and CNN(Heiselberg 2020)](https://www.mdpi.com/776368)**
    - **[Using Sentinel-1 SAR images for Object Detection and Classification](https://www.researchgate.net/publication/342681947_Ship-Iceberg_Detection_and_Classification_in_Sentinel-1_SAR_Images)**
    
    **Notes**<br>
    Calculating total backscatter and cross-polarisation ratio:<br>
    total backscatter: H = HH + HV<br>
    cross-polarisation ratio: C = HV / H<br>

- **[Ship detection in Sentinel-2 RGBs](https://medium.com/the-downlinq/object-detection-in-satellite-imagery-a-low-overhead-approach-part-i-cbd96154a1b7)**



## **[Requirements for the project](https://opencampus.gitbook.io/opencampus-machine-learning-program/projects/requirements)**:

- Presentation of a detailed Jupyter Notebook with code and comment
    - including the definition of the environment
    - including required sections (Introduction, Data and Methods, Results, Baseline)
- A small video, accompanying, for example, a screen recording of the notebook with an explanation of the challenge of the project, the used approach, and the results.
- A statement that the code is released as open source software. The data you use in your project can remain private if you wish.
