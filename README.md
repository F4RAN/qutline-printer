# qutline-controller

```bash
apt update -y && apt upgrade -y && pkg update -y && pkg upgrade && pkg install -y curl && bash <(curl -Ls https://raw.githubusercontent.com/F4RAN/qutline-printer/master/setup/install-termux.sh)
```


## Instructions


# **Tablet and Printer Set Up guide - For Qutline Config**
In order to configure the set up for a store you will need these followings ready:

1. Tablet
1. Printer
1. Extender
1. SIM Card

Once you have all these ready then follow these steps to configure the system.

**Step 1 - Create a Gmail account and set up the tablet**

Every tablet must have a gmail account on it. the naming for these gmails should follow this naming standard:

QutlineTablet#@gmail.com

**Step 2 - Configure the Extender and connect to tablet**

After the set up for tablet is fully done, meaning that the Termux apps, Automate app and the Netshare app are up and running with correct settings, its time to connect the extender to the tablet's hotspot. Proceed
# **Tablet set up**
For the tablet you need to have some basic set up and install 4 applications.

The basic setup is as below:

1. Insert the SIM or Connect tablet to a Wi-Fi
1. Turn developer options on
1. Go to settings -> Display -> screen timeout -> never
1. Uninstall and disable any other unnecessary apps as much as you can
1. Download and install fdroid from https://f-droid.org/en/ and grant permission and access whenever it asked for
1. Use or create a Gmail account and sign it to the Gmail app in the tablet
1. Use or create a Gmail account and sign it to the Gmail app in the tablet
1. Download the file "Qutline Boot.flo" from the email.
1. Download the file "Qutline Boot.flo" from the email.

The apps that should be installed are:

- Termux, Termux:Boot and TermuxAPI
- Automate by LlamaLab
- NetShare by NetShare Softwares

**Termux, Termux:Boot and TermuxAPI**

1. Go to fdroid and search "Termux"
1. Download and install "Termux" and "Termux:Boot" (for Termux:Boot click on Install Anyway when promped) and TermuxAPI (make sure to to allow the location permission after installation)
1. Wait for the installation to finish.
1. Put password 123321 Note that when you type nothing shows on screen because its a password but it will take it. Just input 123321 and then
1. click on the "Enter" keyboard icon on the screen
1. Click on "Allow" if prompted
1. Wait for it to finish then go to the Home screen by pulling up from the bottom of the screen
1. Open Termux:Boot
1. Wait to for the app to load
1. Go to the Home screen again

**Automate**

1. Open Google Play app
1. Search "Automate"
1. Click on the first result
1. Click on Install. Complete account setup if asked. Skip payment if asked for one
1. Click on open
1. Accept the terms
1. Click on the three dots on top right of the screen
1. Click on Import
1. Choose the file "Qutline Boot.flo" or from here:

   ![](Aspose.Words.bbc37fcd-634f-485b-b8a8-997dbf737b97.001.png)

1. Click on "Qutline Boot" flow
1. Add all the privileges except the first one. Allow permissions when asked
1. Click on Start flow and Start it. Grant access when asked
1. Come back to the Home page

**Automate**

1. Open Google Play app
1. Search "Automate"
1. Click on the first result
1. Click on Install. Complete account setup if asked. Skip payment if asked for one
1. Click on open
1. Accept the terms
1. Click on the three dots on top right of the screen
1. Click on Import
1. Choose the file

**Netshare**

1. Open to Google Play
1. Search NetShare
1. Download and Install "NetShare - no-root-tethering"
1. Open the app
1. Make sure you're using the internet of the SIM card and not connected to any Wi-Fi. Also if a Wi-Fi is saved make sure to to click the Setting icon and then click on Forget.
1. click on "Connfigure hotspot" and change the "Network Name" and "Netwrok Password" as below:
1. Network Name: Qutline
1. Network Password: QutlineTablet##123321!
1. While stil in this page, turn on "Bind to Mobile data" and turn off "Usage/Speed Notification"
1. Click on the Back button on top left of the screen
1. Start Wi-Fi Hotspot and allow permissions if asked

Now the tablet is ready to be connected to the extender. Proceed to Extender Connection guide if you need to set up the extender as well.

