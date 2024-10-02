# TakamolAdvancedAI

All the Endpoints are under [API/flask_api.py](API/flask_api.py)

There are two endpoints:
- [chat/casestudy](#en/chat/casestudy)
- [chat/socialmediaplan](#en/chat/socialmediaplan)

### casestudy: 
Generates a case study, target audience, pros and cons, hashtags for the targeted platforms.

### socialmediaplan: 
Generates a social media content plan for the targeted platforms for a period of time (expecting to see 3 posts per week).

**Inputs:**
- **casestudy:** The title and details to make the case study about. (ex. Palm Hills in October in Egypt)
- **socialmediaplan:** The period of time that the plan will work through, and the targeted platforms. (ex. Generate the social media content plan for a period of 3 weeks for Facebook, Instagram, Twitter, and LinkedIn)

# Endpoints:

## English:
- [/en/chat/casestudy](#en/chat/casestudy): English case study
- [/en/chat/socialmediaplan](#en/chat/socialmediaplan): English Social Media Plan
- [/en/prompt-generator](#en/prompt-generator): Generate English Prompt from post content
- [/en/prompt-enhancer](#en/prompt-enhancer): Enhance English Prompt
- [/en/image-analyzer](#en/image-analyzer): Analyze Images and generate English prompts

## Arabic:
- [/ar/chat/casestudy](#ar/chat/casestudy): Arabic case study
- [/ar/chat/socialmediaplan](#ar/chat/socialmediaplan): Arabic Social Media Plan
- [/ar/prompt-generator](#ar/prompt-generator): Generate Arabic Prompt from post content
- [/ar/prompt-enhancer](#ar/prompt-enhancer): Enhance Arabic Prompt
- [/ar/image-analyzer](#ar/image-analyzer): Analyze Images and generate Arabic prompts

## Combine:
- [/image](#image): Create image

# AI Investment:
- [/ar/investment-residential-building](#ar/investment-residential-building): Create an investment consultation for a residential building
- [/ar/investment-residential-commercial-building](#ar/investment-residential-commercial-building): Create an investment consultation for a residential commercial building
- [/ar/investment-commercial-building](#ar/investment-commercial-building): Create an investment consultation for a commercial building
- [/ar/investment-shopping-mall](#ar/investment-shopping-mall): Create an investment consultation for a shopping mall
- [/ar/investment-villas](#ar/investment-villas): Create an investment consultation for villas
- [/ar/investment-villa](#ar/investment-villa): Create an investment consultation for a villa
- [/ar/investment-residential-compound](#ar/investment-residential-compound): Create an investment consultation for a residential compound
- [/ar/investment-administrative-building](#ar/investment-administrative-building): Create an investment consultation for an administrative building
- [/ar/investment-hotel](#/ar/investment-hotel): Create an investment consultation for a hotel