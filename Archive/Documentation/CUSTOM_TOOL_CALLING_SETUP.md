# Custom Tool Calling Setup for DNA-Expert Model

**Status:** Ready to implement  
**Date:** November 30, 2025

Since the DNA-expert fine-tuned model doesn't support OpenAI function calling, we're implementing XML-based tool calling + markdown rendering.

---

## 🔧 **Part 1: LM Studio Configuration**

### **Step 1.1: Set Prompt Template to Jinja**

In LM Studio:
1. Go to **model chat**
2. Click **Settings** (gear icon)
3. Find **Prompt Format** dropdown
4. Select **Custom (Jinja)**
5. A text box will appear labeled "Jinja Template"

### **Step 1.2: Paste This Jinja Template**

Copy and paste this entire block into the Jinja Template field:

```jinja
{{- bos_token }}
{%- if messages[0]['role'] == 'system' %}
<|im_start|>system
{{ messages[0]['content'] }}
{%- if tools %}

# Available Tools
You can call these tools to get real data from the LexRAG 4.4B genomic database:

{% for tool in tools -%}
- {{ tool.function.name }}: {{ tool.function.description }}
{% endfor %}

To use a tool, output XML tags like this:
<tool_call>
<name>analyze_gene</name>
<arguments>{"gene_symbol": "MLH1"}</arguments>
</tool_call>

You can call multiple tools. When you have the data you need, give your final answer without tool tags.
{%- endif %}
<|im_end|>
{% endif %}
{%- for message in messages[1:] %}
{%- if message.role == 'user' %}
<|im_start|>user
{{ message.content }}<|im_end|>
{%- elif message.role == 'assistant' %}
<|im_start|>assistant
{{ message.content }}<|im_end|>
{%- elif message.role == 'tool' %}
<|im_start|>tool
Tool Result:
{{ message.content }}<|im_end|>
{%- endif %}
{%- endfor %}
<|im_start|>assistant
```

### **Step 1.3: Keep Your Excellent System Prompt**

Your current system prompt is perfect! Keep it exactly as is. The Jinja template will:
- Inject tool definitions when provided
- Tell the model to use XML format
- Keep your DNA expertise intact

### **Step 1.4: Reload the Model**

After changing the template:
1. Unload the model
2. Reload it
3. This ensures the new template takes effect

---

## 💻 **Part 2: Backend Already Updated**

I've already updated the backend to:
- ✅ Send tools in OpenAI format (LM Studio converts via Jinja)
- ✅ Parse XML `<tool_call>` blocks from model responses
- ✅ Execute tools and feed results back
- ✅ Strip tool XML from final user-facing responses
- ✅ Strip "system" prefix

**No action needed - backend is ready!**

---

## 🎨 **Part 3: Frontend Markdown Rendering** (Optional but Recommended)

### **Step 3.1: Install Markdown Parser**

Run in terminal:
```bash
cd d:/LexAI3/lexui
npm install marked
npm install @types/marked --save-dev
npm install @tailwindcss/typography
```

### **Step 3.2: Update App.tsx**

Add at top:
```typescript
import { marked } from 'marked';
```

Add parsing function:
```typescript
const parseMarkdown = (text: string): string => {
  // Strip "system" prefix
  text = text.replace(/^system\s*\n+/, '');
  // Parse markdown to HTML
  return marked.parse(text) as string;
};
```

Replace message content rendering (around line 207):
```typescript
{/* OLD: */}
<p style={{...}}>{message.content}</p>

{/* NEW: */}
<div 
  style={{margin: 0, fontSize: '14px', lineHeight: '1.5'}}
  dangerouslySetInnerHTML={{ __html: parseMarkdown(message.content) }}
/>
```

### **Step 3.3: Add Tailwind Typography Plugin**

Update `tailwind.config.js`:
```javascript
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography')
  ],
}
```

---

## 🧪 **Testing the New Setup**

### **After applying all changes:**

1. **In LM Studio:**
   - Jinja template applied ✓
   - Model reloaded ✓

2. **Test with:**
```bash
cd d:/LexAI3
python test_simple.py
```

3. **Expected output:**
   - Model should output `<tool_call>` XML blocks
   - Backend parses them
   - Executes the tools
   - Returns data to model
   - Model synthesizes final answer

4. **In browser (after markdown setup):**
   - Headers render as headers
   - Bold text actually bold
   - Lists have bullets
   - Much cleaner, professional look

---

## 📋 **Quick Start Checklist:**

- [ ] Paste Jinja template into LM Studio
- [ ] Reload model in LM Studio
- [ ] Run `npm install marked @types/marked @tailwindcss/typography` in lexui folder
- [ ] Update App.tsx with markdown parsing
- [ ] Update tailwind.config.js
- [ ] Restart frontend (`npm run dev`)
- [ ] Test with `python test_simple.py`

---

## 🎯 **Expected Behavior:**

**User:** "What is MLH1?"

**Model outputs:**
```
<tool_call>
<name>analyze_gene</name>
<arguments>{"gene_symbol": "MLH1"}</arguments>
</tool_call>
```

**Backend:**
- Parses XML
- Calls genomics API
- Gets MLH1 data from 4.4B records
- Sends back to model

**Model final response:**
```
MLH1 is a DNA mismatch repair gene...
(with real data from the genomics database)
```

**Frontend displays:**
- Clean HTML rendering
- No markdown symbols
- Professional formatting

---

**Ready to implement! Start with the Jinja template in LM Studio, then let me know if you want me to add the markdown rendering to the frontend!** 🚀



