## VR Audience Fire/Water

## Marketplace

https://python1320.gumroad.com/l/fire

### Description

Catch on low poly fire in VR, get extinguished by water sprays and drip water.

![avatar caught on fire](docs/toastacuga-on-fire-optimized.png)

### Includes
 
 - Installation instructions
 - VRCFury Unity Avatar drag-and-drop prefab

### Requirements

 - SteamVR
 - Windows (might work on linux)
 - VRChat (ChilloutVR should also work, but is not documented and probably no longer needed. Resonite also does not need this addon.)
 - Some knowledge about [OSC](https://docs.vrchat.com/docs/osc-overview)
 - Your custom avatar source code. Used in examples: [TongueyToastacuga by 'a distraction'](https://drive.google.com/drive/folders/1ekIiFBnzJNhH2a6wwYLo2s5G-VuUlIY5)
 - [Unity editor](https://creators.vrchat.com/sdk/current-unity-version/) for avatars 
 - [VRCFury](https://vrcfury.com/getting-started)

### Test Avatar

https://vrchat.com/home/avatar/avtr_48cccc45-f524-4a8a-9521-368252334959

### Compatible addons 

These addons can extinguish you or make you catch on fire (be warned!)

 - [Spray Bottle for VRC](https://jinxxy.com/market/listings/3292261612823512778) (free)
 - [Fire-Breathing & Flame Sneeze](https://violentpainter.gumroad.com/l/vfx-firebreathing)

TODO: Better fire particle addon

### Installation Video

[Using VRCFury prefab assets in Unity](https://www.youtube.com/watch?v=QDvzfLa82yI)

### Installation Instructions

The steps are mostly the same as here https://morghus.gumroad.com/l/cugahoodie (replace with vr_audience_fire.unitypackage)

**Unity**

 1. Install [VRCFury](https://vrcfury.com/getting-started)
 2. Download the gumroad `vrpets` package and extract it
 3. TAKE A BACKUP OF YOUR AVATAR HERE
 4. Import the downloaded `.unitypackage`: 
   - double click the package
   - ... or in Unity: Menu Assets -> Import Package -> Custom Package
 5. Drag the imported prefab into the scene
   - Locate the vrpets directory in the Project tab, within you'll find a "vrpets" object. 
      - Click and drag it onto the main Avatar object in your Hierarchy. It should be a direct child of the object.
	  - Once the prefab has been put in the correct place, it should show up on your avatar in the Scene view.
	  - The package includes a script that will automatically setup sounds to correct hand bones. No manual setup should be necessary.
      - Do not disable the "VRPets Prefab" object itself as the pets will not work properly
 6. Run build and test or republish your avatar
 7. Remember to enable OSC and to regenerate OSC config!

  - VRCFury will automatically add a new [expression menu](https://docs.vrchat.com/docs/action-menu#expression-menu) entry and you will be able to toggle the fire on and off there. Test it in game and see if it works. 

**App**
 1. Extract the latest zip file into a folder, launch the executable.
 2. Launch VRChat
 3. Launch the executable in the extracted folder
 4. If everything goes right the executable should detect vrchat and install itself into SteamVR (if running)
 5. Test avatar does not have a flame thrower yet, you need someone else to make you catch on fire

### Troubleshooting

 1. Ensure you have Avatar Self Interact enabled in the VRChat settings menu: ![img/self-interact.png](img/self-interact.png)
 2. [Enable OSC](https://docs.vrchat.com/docs/osc-overview#enabling-it)
 3. Use [OSC Debug](https://docs.vrchat.com/docs/osc-debugging) to see if are receiving any data
 4. Make sure your VRChat SDK is updated in the companion app! VRCFury usually requires the latest VRChat SDK.

### Known Issues

https://github.com/python1320/vr_audience_fire/issues

### How to change the sounds

 - Navigate to the prefab and into the fire and just replace the sound file with your own

### NO SUPPORT NO WARRANTY

This is a hobby for me, paying only gives you access to the asset files. Payment does not give support. I may or may not have time to look at github issues but that's about it.
No warranty of any kind!
I cannot afford supporting you, and you cannot afford my support, sorry. Feel free to ask someone else to fix things for you.
