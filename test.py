history = [
    {
        "role": "user",
        "content": "tell me a joke"
    }
]

new_content =   { 
                    "role": "assistant",
                    "content": "Under the soft glow of the moon, Luna the unicorn danced through fields of twinkling stardust, leaving trails of dreams for every child asleep.",
                    "refusal": None
                }
new_content_2 = { "role": "user", "content": "tell me another" }

history.append(new_content)
history.append(new_content_2)
print(history)