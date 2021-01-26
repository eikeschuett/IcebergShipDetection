# IcebergShipDetection
- Topic: Iceberg and ship detection in satellite imagery
- Goals: The project goal is to build an algorithm for the detection of ships and icebergs in Sentinel-1 SAR imagery. Desired output is a map, which shows the locations of icebergs, ships and unidentified objects.
- Details: The dataset used for training is obtained from a Kaggle challenge, [Statoil/C-CORE Iceberg Classifier](https://www.kaggle.com/c/statoil-iceberg-classifier-challenge). Each image has 75x75 pixels with two bands from HH and HV polarisations and contains a ship or an iceberg. This dataset will be used to train a CNN.
        After training the classification model, we will use Sentinel-1 SAR images to show the "real world application" of our model. The satellite images will be pre-processed with the Sentinel Application Platform (SNAP) Python API. We will then identify bright objects within each satellite image. A 75x75 subset of the radar image will be made for each object and fed into our classification model. Finally, the results will be plotted on a map.
  
## Testscenes and AIS Ship Positions
- Disko Bay
    - S1A_IW_GRDH_1SDH_20210115T100027_20210115T100052_036147_043CF4_049C
        - Other Type/Auxillary N69°08.750' W53°39.933'
        - Fishing Vessel N68°45.080' W51°20.846'

    - S1B_IW_GRDH_1SDH_20210114T100803_20210114T100828_025149_02FE89_234D
        - Other Type/Auxillary N69°05.990' W53°18.654'
        - Fishing Vessel N68°51.626' W52°47.673'
        - Other Type/Auxillary N69°23.972' W51°36.317'
        - Fishing Vessel N68°43.877' W51°30.219'
        - Fishing Vessel N68°43.825' W51°21.114'
        - Cargo Ship N76°28.180' W54°08.052'
- Svalbard
    - S1B_IW_GRDH_1SDH_20210108T154500_20210108T154525_025065_02FBC6_38D2 (contains only a tanker and no icebergs)
        - Tanker N78°12.417' E14°32.650'
  
## Links

### Preprocessing with Snappy
- **[Some code on Github](https://github.com/wajuqi/Sentinel-1-preprocessing-using-Snappy)**
- **[ESA Webinar](https://www.youtube.com/watch?v=PiU68g3WRIY)**
- [Suggesting processing workflow with SNAPPY on step forum](https://forum.step.esa.int/t/radiometric-geometric-correction-workflow/2540/35)

### Object Detection and Models
- **[Short article and code of another solution for the kaggle contest on towardsdatascience.com](https://towardsdatascience.com/deep-learning-for-iceberg-detection-in-satellite-images-c667acf4bad0)**
- **Ship-Iceberg Classification**
    - **[Using SAR and Multispectral Satellite Images with SVM and CNN (Heiselberg 2020)](https://www.mdpi.com/776368)**
    - **[Using Sentinel-1 SAR images for Object Detection and Classification (Heiselberg 2020)](https://www.researchgate.net/publication/342681947_Ship-Iceberg_Detection_and_Classification_in_Sentinel-1_SAR_Images)**
    
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
- Time: 8 -- 10 minutes
