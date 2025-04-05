# Thing Pinball Machine

A complete Mission Pinball Framework (MPF) implementation of "Thing" pinball machine.

## Installation and Setup

1. Install Mission Pinball Framework. Follow the instructions at: https://missionpinball.org/install/
2. Unzip this package to a folder on your computer
3. Navigate to the folder in a terminal/command prompt
4. Run MPF:
   ```
   mpf both
   ```

## Machine Overview

This pinball machine implements a comprehensive game flow based on a flowchart with multiple game modes:

- **Dog Hunt**: Spell "DOG" and hit the spinner 100 times
- **Discovery**: Hit the pop bumpers 100 times and complete the left ramp
- **Infected**: Hit the left ramp 3 times and complete the DOG targets
- **Blood Test**: Make 3 Newton ball shots and hit the left ramp
- **Spider Head**: Hit the spinner 50 times and complete the left ramp
- **Wizard Mode**: Hit pop bumpers and detonate the TNT
- **Ball Lock**: Lock 3 balls by completing left ramp shots and then shooting the right ramp
- **Multiball**: Release locked balls and collect jackpots

## Game Rules

- Game modes must be completed in sequence as shown in the flowchart
- Only one game mode can be active at a time
- Modes cannot be repeated once complete, unless they were not completed successfully
- All modes reset after Wizard Mode is completed
- The game supports 1-4 players

## Service Mode

Press `F2` at any time to enter Service Mode. This allows you to:

1. Test all switches
2. Test all coils
3. Test all lights
4. Exit service mode

## Hardware Configuration

The game is configured to work with a Fast Pinball Neuron Controller. The hardware map includes:

- Trough with 7 ball slots
- 3-bank drop targets for "DOG"
- Ramps, orbits, and special shots
- Ball lock mechanism for multiball
- Slingshots, pop bumpers, and other standard playfield elements

## Keyboard Controls

- `S`: Start button
- `Z`: Left flipper
- `/`: Right flipper
- `[1-7]`: Trough switches
- `D`, `O`, `G`: DOG targets
- `L`: Shooter lane
- `R`: Right ramp
- `V`: Left ramp
- Other keys as mapped in `machine.yaml`

## File Structure

The MPF configuration follows standard MPF practices with mode-based configuration:

- `/config.yaml`: Main configuration file
- `/machine.yaml`: Machine-specific settings
- `/modes/`: Game mode configurations
  - Each mode has its own folder with configuration and code

## Credits

Created with Mission Pinball Framework (MPF)
