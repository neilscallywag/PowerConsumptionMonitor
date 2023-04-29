# Project Title

The goal of this project is to estimate the power consumption of running processes on a computer. This document will provide an overview of the code base and how to use it. It uses the standard power formula to estimate the power consumption i.e 
```math
P=\frac{1}{2}CV^2\alpha+P_{static}
```
where α stands for the activity factor for both the GPU and the CPU.  



## Code Base Overview

The code base consists of three main components: the PowerModel, PowerView, and PowerController. It is based on the MVC architecture. 

### PowerModel

The PowerModel is responsible for estimating the power consumption of a running process. It utilizes the psutil and GPUtil libraries to collect data on the system and running processes, and then uses this data to estimate the power consumption. 

We first obtain the clock frequency, number of cores, supply voltage, and temperature of the computer's CPU and GPU. It then estimates the power consumption of the CPU and GPU by calculating the dynamic and static power and summing them up. 

The dynamic power is estimated based on the activity factor of the CPU and GPU, which is calculated by monitoring their usage over a certain period of time. The static power is estimated using a constant values given a processor and temperature assumptions.

The calculations are performed differently for windows and linux as linux has more available options in the psUtil library to determine some of the constants like voltage and temperature. 

Ideally we would want to be able to replace those constants and assumptions with actual values. However, there are no libraries available to get the hardware information. We would require users to input them accordingly. 
### PowerView

The PowerView is responsible for displaying the running processes and allowing the user to select a process to estimate power consumption. It utilizes the tkinter library to create a graphical user interface.

### PowerController

The PowerController is responsible for connecting the PowerModel and PowerView. It collects the data on running processes from the PowerModel and passes it to the PowerView to display.

## Installation

1. Clone the project repository.
2. Install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```
It would be reccomended to install the dependencies in  virtual environment using venv or conda. 
