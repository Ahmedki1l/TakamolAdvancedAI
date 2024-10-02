# TakamolAdvancedAI

All the Endpoints are under API/flask_api.py

there are two endpoints: chat/casestudy chat/socialmediaplan
casestudy: generates a case study, target audience, pros and cons, hashtags for the targeted platforms
socialmediaplan: generates a social media content plan for the targeted platforms for a period of time ( expecting to see 3 posts per week ).

Inputs: 
-casestudy: the title and details to make the case study about. ( ex. Palm Hills in October in Egypt )
-socialmediaplan: the period of time that the plan will work through, and the targeted platforms. ( ex. generate the sociak media content plan for a period of 3 weeks for Facebook, Instagram, Twitter, and LinkedIn )


# Endpoints:
## English:
- /en/chat/casestudy: English case study
- /en/chat/socialmediaplan: English Social Media Plan
- /en/prompt-generator: Generate English Prompt from post content
- /en/prompt-enhancer: Enhance English Prompt
- /en/image-analyzer: Analyzing Images and generating English prompt about it

## Arabic:
- /ar/chat/casestudy: Arabic case study
- /ar/chat/socialmediaplan: Arabic Social Media Plan
- /ar/prompt-generator: Generate Arabic Prompt from post content
- /ar/prompt-enhancer: Enhance Arabic Prompt
- /ar/image-analyzer: Analyzing Images and generating Arabic prompt about it

## Combine:
- /image: Create image

# AI Investment:
- /ar/investment-residential-building: create an investment consultation for a residential building
- /ar/investment-residential-commercial-building: create an investment consultation for a residential commercial building
- /ar/investment-commercial-building: create an investment consultation for a commercial building
- /ar/investment-shopping-mall: create an investment consultation for a shopping mall
- /ar/investment-villas: create an investment consultation for villas
- /ar/investment-villa: create an investment consultation for villa
- /ar/investment-residential-compound: create an investment consultation for a residential compound
- /ar/investment-administrative-building: create an investment consultation for an administrative building