# [Design Studio](https://vanderbilt.design): Your Print is Ready
[![Build Status](https://travis-ci.org/vanderbilt-design-studio/your-print-is-ready.svg?branch=master)](https://travis-ci.org/sameer/your-print-is-ready)
[![Coverage Status](https://coveralls.io/repos/github/vanderbilt-design-studio/your-print-is-ready/badge.svg?branch=master)](https://coveralls.io/github/sameer/your-print-is-ready?branch=master)

## Overview 
"Your Print is Ready" is a project that seeks to improve the 3D printing workflow at the Design Studio (DS). Several DS mentors were interviewed to identify printing habits and pain points. From these interviews, one overarching problem of interest was identified: you have to be physically present to know printer and print job status. This project aims to alleviate it by enabling both mentors and users to query printer and print job status remotely.

The project will be partitioned into phases, each containing milestones. Users will be involved throughout the design process to ensure the project does not stray from solving the issue at hand. User testing and feedback will be used to judge the success of the project.

# Requirements

In short, this project should result in a product that displays the status of all printers in the Design Studio and informs users if their print succeeds or fails.

Identified Goals:
* Future-proofness: the product should work...
	* Regardless of who must develop it
		* Write it in a language that is taught at Vanderbilt: ~~C++ is the language of choice, any CS major here should be able to use it. While I would prefer to write it in Rust myself and we learned Clojure in this class, it is a bad idea to throw it onto future maintainers.~~ I had to write it in Python because it is the language of choice for development on Raspberry Pi, I was worried about memory leak related issues, setting up cross-compiling is a nightmare, and the APIs I found for using websockets in C++ were insanely complex for a project of this scope.
	* Regardless of the number of printers in the Design Studio
	* As long as all printers are Ultimaker 3 printers. 
		* New printers will require implementation of communication methodology with those printers.
	* As long as they are all on the same network.
		* I don't anticipate a situation where this will change. If it does, a VPN should be used to join the networks and protect the printers.
* Inform users about print success or failure
	* Text would be great, but as it stands, the DS doesn't collect phone numbers, so an email-based system is ideal.
	* All Ultimaker 3 printers have a camera with mjpg video stream capabilities, a picture of the print success or failure could be included.
	* We record print information in a manner separate to the way prints are sent, so some heuristic manner of matching the two is needed.
* Inform users about generic printer status
	* This is fairly straightforward; all Ultimaker 3 printers have an API you can call to query their status
	* Getting print "color" will be much harder. This would require that mentors themselves record the current color. This will not be part of the prototype. What could be done for long-term correctness is computer vision could be used to analyze the jpeg video stream when mentors load new filament spools to edge-detect the build-plate, flood-fill the filament extrusion shape and use that as the filament color.
	* Naming the printers will be a challenge -- you can name them in the software on the Design Studio computer, but those don't show up on the printers themselves.

# Development Approach

Your Print is Ready will be developed using [Kanban](https://en.wikipedia.org/wiki/Kanban_(development), an agile methodology. This is an appropriate approach considering that the scope of the project and timeline is well-defined. Kanban doesn't try to prescribe any inter-team-communication practices, which is important considering that the team only has one member, myself. 
Tasks will be split up into three main stages: 
* to-do
* doing
	* planning
	* development (TDD)
	* testing
		* integration
		* user acceptance
	* deployment
		* beta
		* prod
* done

All tasks are atomic to the point that they are based on a user story. Tasks based on epics in to-do must be split into more atomic tasks during the planning phase.
In the development stage, actual implementation will be done, following test-driven driven development practices.
While the next stage is called testing, my intention is that it will cover more time-consuming tests, where I have to integrate with existing Design Studio infrastructure or work with users to ensure that the project will meet the needs I set out to meet. Anything that doesn't meet user needs will return to the development stage for modification as per user feedback.
The deployment stage involves releasing the results of a task to a beta stage, then further production once some users have had a chance to test it a bit.
The done stage is simple and only occurs once the results of a task are all released to production.

# Results: Project Succeeded and is Launched

## Presentation 
I presented it to CS5278 on 10/23/18 at 11:50AM. You can [view the presentation](https://github.com/vanderbilt-design-studio/your-print-is-ready/blob/master/presentation.pdf).

## See it yourself
Generic printer status is now available on the [Design Studio Website](https://vanderbilt.design)
