# Solution for the Adversarial Machine Learning CTF

This repository shows a solution for the [Adversarial Machine Learning CTF](https://github.com/arturmiller/adversarial_ml_ctf).

## The vulnerability
You should run and open the website with a normal browser. Allow the website to use your real or [fake](https://github.com/arturmiller/adversarial_ml_ctf#i-have-no-webcam) webcam. You can see, that for the webcam images similarity values are provided. This value is the certainty of the machine learning model, which tries to classify if you are a person who is allowed to enter. That this is value is visible is the actual vulnerability. Such a value should not be provided to the user, because it can be used in an attach, where an adversarial image is created by an optimization procedure. The idea is to change an initial image gradually and keep only the changes if the similarity of the new image is higher than of the old one.  
In general it should be considered, that this optimization problem is hard to solve, because there is there is no gradient and the number of dimensions (number of pixel) is very high. However Neural Networks are [prone to adversarial images](https://arxiv.org/abs/1412.6572). The whole image space is full of these adversarial images. Therefore it should not be so hard to find just one of them.

## Solution
If you look into the source code of the website with chromes of firefox developer tools, you will see in [webcam.js](https://github.com/arturmiller/adversarial_ml_ctf/blob/master/app/static/webcam.js#L34), that a POST request is used to send an image of the webcam to the server. The response contains the similarity value. You could find this information, by using an intercepting web proxy like Burp Suite as well. The similarity of a given image could now be checked with a script using Python and the Request library.  
In the solution the optimization is initialized with a white image. The idea is to sample one pixel and one channel (RGB) and change its value randomly (0, 255). If the updated image has a higher similarity than the old one it will be kept, otherwise it will be discarded. This is done iteratively until the similarity is high enough (>80%). Then the Neural Network gives us access to the website.  
I have implemented the solution, the way I described, however the optimization takes a very long time. I found a trick to speed it up. All images with some kind of content have most of their information in the lowest frequencies. This is the basic idea behind why image compression works. So I have downsampled the image by a factor of 32. Then one pixel of the image is changed, as previously described. The resulting image is upsampled so that it can be processed by the Neural Network. This trick reduces the optimization time enormously.
You can find the source code of the solution in [optimize.py](https://github.com/arturmiller/adversarial_ml_ctf_solution/blob/master/optimize.py).

## Results
If you want replicate the "attack" start the webserver and run optimize.py.
```bash
python3 optimize.py
```
It takes only a few seconds until the script finishes. You should see, that the similarity is increasing until it reaches 80%. At 80% the webserver responses with a redirect. The url is "http://localhost:5000/hidden_page_281685775888171188986444381606". In your case the number is be different, because it is randomly generated. This should ensure that this page cannot be found with a brute force attack.  
Finally the script creates two images, showing the optimization graph and the resulting adversarial image. In my case they looked like this.  
![adversarial image](https://raw.githubusercontent.com/arturmiller/adversarial_ml_ctf_solution/master/images/adversarial_image.png)  
![similarity](https://raw.githubusercontent.com/arturmiller/adversarial_ml_ctf_solution/master/images/similarity.png)

## Background information
The neural network is a [ResNet50](https://arxiv.org/abs/1512.03385). It was trained on a dataset with 1000 classes called Imagenet. The similarity value of this challenge is the probability of the image belonging to the class "goldfish". I didn't want to put the effort into training a Neural Network from the ground up, if it is not necessary to show the actual vulnerability. Since the Neural Network just tries to recognize goldfishes, you could simply solve the challenge by showing the Neural Network a goldfish, however this is not the idea of this challenge. I think it is quite interesting, that the Neural Network, which is still one of the best in the world, can be fooled so easily. The adversarial image does not look like a goldfish at all. 
