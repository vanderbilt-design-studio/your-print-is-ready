# [Design Studio](https://vanderbilt.design): Your Print is Ready
[![Build Status](https://travis-ci.org/sameer/your-print-is-ready.svg?branch=master)](https://travis-ci.org/sameer/your-print-is-ready)

"Your Print is Ready" is a project that seeks to improve the 3D printing workflow at the Design Studio (DS). Several DS mentors were interviewed to identify printing habits and pain points. From these interviews, one overarching problem of interest was identified: you have to be physically present to know printer and print job status. This project aims to alleviate it by enabling both mentors and users to query printer and print job status remotely.

A text-messaging-based application will be created as a part of the project. It will be written in Clojure, using AWS for computation and Twilio for the transmission and receipt of text messages. To collect printer-related information, a computer in the DS will be used to query printers and transmit information to AWS.

The project will be partitioned into phases, each containing milestones. Users will be involved throughout the design process to ensure the project does not stray from solving the issue at hand. User testing and feedback will be used to judge the success of the project.

# Questions:
1. How often do you print at the Design Studio?
2. Have you ever come in during off-hours to print? On-hours?
3. Has there ever been a time when you wanted to print, but all the printers were in use? What did you do?
4. Would being able to check printer status from your mobile device be helpful?
5. How do you find out when your print succeeds or fails?
6. Would receiving text notifications about print success or failure be helpful?
7. When your print fails, do you try to re-print it? If so, how?
8. Do printers sometimes have colors you dislike?
9. Where do most of your prints come from?
10. What are the pros and cons of printing at the Design Studio as compared to printing at the Engineering & Science Building (ESB) Makerspace?

# Answers:

## Question 1:
* Once every few months
* A few times a semester
* Once a month

## Question 2:
* Yes, yes
* Try to print during my shift b/c I'm usually in the Studio at that time, but they usually finish during off-hours
* Both

## Question 3:
* Left and came back another time during off-hours
* Yes, ended up queueing up the print so when it finished I could do mine
* I left, came back and tried to print when I was free

## Question 4:
* Yes
* Yes, super helpful, if I knew I had to print wouldn't have to walk all the way here
* That would be so cool

## Question 5:
* Come back to the Design Studio and check to see if it is on the print table or in one of the printers
* Come and talk to the mentor or see if it's on the table
* Check the table if it's there or if it's on the printer

## Question 6:
* Yes, but it would be a lot of work for mentors to keep track of
* Yes, that way I wouldn't have to walk all the way here, especially during freshman year b/c I was way further away
* That would be cool too

## Question 7:
* Check the part to see if it's a part issue or a printer issue. If it's a part issue, I might re-use the same printer, or a different printer otherwise.
* Try to re-print it, but it takes me a lot longer to get around to printing it the second time
* Yeah, try to re-print tha part but will try to re-design it if it failed for reasons due to the part

## Question 8:
* Yes, the flesh color, it's unnatural and concerns me. I'm not a big fan of the yellow filament either.
* Brown
* I like the plain whites, the bright colors aren't my favorite because it doesn't look that great on important projects, neutral colors are best.

## Question 9:
* Thingiverse
* Design them on Tinkercad
* Make them all myself

## Question 10:
* You don't have to wait in a queue at the Design Studio. The ESB on the other hand has higher print quality and dissolvable supports (not that necessary for my purposes). The Design Studio operates on student hours, since Featheringill Hall is open 24/7 so it can tend to have better hours, and it's more central. The ESB has more standard colors.
* Prefer DS because it's more easy-going, you have to go through safety training for the ESB and if their times don't match you can't really get that training. DS is also more central on main campus.
* DS feels homier, more welcoming to work in. Makerspace has some cool tools like foam cutter but I don't expect them to be here. I like the diverse set of tools, heard the electronic makerspace is fantastic but I've never used it.

# Requirements

In short, this project should result in a product that displays the status of all printers in the Design Studio and informs users if their print succeeds or fails.

Identified Goals:
* Future-proofness: the product should work...
	* Regardless of who must develop it
		* Write it in a language that is taught at Vanderbilt: C++ is the language of choice, any CS major here should be able to use it. While I would prefer to write it in Rust myself and we learned Clojure in this class, it is a bad idea to throw it onto future maintainers.
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
