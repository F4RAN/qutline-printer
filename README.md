# qutline-controller

```bash
apt update -y && apt upgrade -y && pkg update -y && pkg upgrade && pkg install -y curl && bash <(curl -Ls https://raw.githubusercontent.com/F4RAN/qutline-printer/master/setup/install-termux.sh)
```


## Instructions
In order to configure the set up for a store you will need these followings ready:

Tablet

Printer

Extender

SIM Card

Once you have all these ready then follow these steps to configure the system.

 

Step 1 - Create a Gmail account and set up the tablet

Every tablet must have a gmail account on it. the naming for these gmails should follow this naming standard:

QutlineTablet#@gmail.com

 

Step 2 - Configure the Extender and connect to tablet

After the set up for tablet is fully done, meaning that the Termux apps, Automate app and the Netshare app are up and running with correct settings, its time to connect the extender to the tablet's hotspot. Proceed

 

 

 

 

Tablet set up
For the tablet you need to have some basic set up and install 4 applications.

 

The basic setup is as below:

Insert the SIM or Connect tablet to a Wi-Fi

Turn developer options on

Go to settings -> Display -> screen timeout -> never

Uninstall and disable any other unnecessary apps as much as you can

Download and install fdroid from https://f-droid.org/en/ and grant permission and access whenever it asked for

Use or create a Gmail account and sign it to the Gmail app in the tablet

Use or create a Gmail account and sign it to the Gmail app in the tablet

Download the file "Qutline Boot.flo" from the email.

Download the file "Qutline Boot.flo" from the email.

 

The apps that should be installed are:

Termux, Termux:Boot and TermuxAPI

Automate by LlamaLab

NetShare by NetShare Softwares

 

 

 

Termux, Termux:Boot and TermuxAPI

Go to fdroid and search "Termux"

Download and install "Termux" and "Termux:Boot" (for Termux:Boot click on Install Anyway when promped) and TermuxAPI (make sure to to allow the location permission after installation)

Wait for the installation to finish. 

Put password 123321 Note that when you type nothing shows on screen because its a password but it will take it. Just input 123321 and then 

click on the "Enter" keyboard icon on the screen

Click on "Allow" if prompted 

Wait for it to finish then go to the Home screen by pulling up from the bottom of the screen

Open Termux:Boot

Wait to for the app to load

Go to the Home screen again

 

 

Automate

Open Google Play app

Search "Automate"

Click on the first result

Click on Install. Complete account setup if asked. Skip payment if asked for one

Click on open

Accept the terms

Click on the three dots on top right of the screen 

Click on Import

Choose the file "Qutline Boot.flo" or from here: 

Qutline Boot.flo

 

 Click on "Qutline Boot" flow

Add all the privileges except the first one. Allow permissions when asked

Click on Start flow and Start it. Grant access when asked

Come back to the Home page

 

 

Automate

Open Google Play app

Search "Automate"

Click on the first result

Click on Install. Complete account setup if asked. Skip payment if asked for one

Click on open

Accept the terms

Click on the three dots on top right of the screen 

Click on Import

Choose the file 

 

 

Netshare

Open to Google Play

Search NetShare

Download and Install "NetShare - no-root-tethering"

Open the app

Make sure you're using the internet of the SIM card and not connected to any Wi-Fi. Also if a Wi-Fi is saved make sure to to click the Setting icon and then click on Forget.

click on "Connfigure hotspot" and change the "Network Name" and "Netwrok Password" as below:

Network Name: Qutline

Network Password: QutlineTablet##123321!

While stil in this page, turn on "Bind to Mobile data" and turn off "Usage/Speed Notification"

Click on the Back button on top left of the screen

Start Wi-Fi Hotspot and allow permissions if asked

Now the tablet is ready to be connected to the extender. Proceed to Extender Connection guide if you need to set up the extender as well.

