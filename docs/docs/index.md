![Chassis logo](images/chassis-positive.png){: style="width:200px; margin-bottom:10px;" }
#Build ML-friendly Containers. Automatically.
Turn machine learning models into portable container images that can run just about anywhere.
``` py
pip install chassisml
```
**Create a model**
``` py
# Create Chassisml model
chassis_model = chassis_client.create_model(context=context,process_fn=process)
```
**Create and publish an image of your model**
``` py
# Publish model to Docker Hub
response = chassis_model.publish(
    model_name="Chassisml Regression Model",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
) 
```

**Serve your model whereever containers run**
<style>
#container {
  border: none;
  height: 75px;
  text-align: justify;
  -ms-text-justify: distribute-all-lines;
  text-justify: distribute-all-lines;
  /* just for demo */
  min-width: 612px;
}

.box1,
.box2,
.box3,
.box4 {
  width: 150px;
  height: 125px;
  vertical-align: top;
  display: inline-block;
  *display: inline;
  zoom: 1
}

.stretch {
  width: 100%;
  display: inline-block;
  font-size: 0;
  line-height: 0
}

.box1,
.box3 {
  /*background-image:url("images/kserve.png")*/
}

.box2 img{
  width: 50%;
  text-align: auto
}

.box4 {
  /*background-image:url("images/docker.png")*/
}
</style>

<div id="container">
  <div class="box1"><img src="images/docker.png" ></div>
  <div class="box2"><img src="images/kserve.png" ></div>
  <div class="box3"><img src="images/modzy.png" ></div>
  <div class="box4">More coming soon...</div>
  <span class="stretch"></span>
</div>

##Try it Yourself
Create an account [here] at chassis.modzy.com to start building your own ML containers (or check out [Deploy Chassis](tutorials/devops-deploy.md) to host an instance on a private k8s cluster).
