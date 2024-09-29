This project contains various efforts to augment gospel study.

The sermons folder contains drafts of my own general conference quality discourses on topics that are meaningful to me, starting with my talk on repentance given in Springville, Jan 2024.

The scriptures_db folder contains code to analyze the scriptures using various practices of computational literary analysis.

Use this link to convert .md to .pdf: https://www.markdowntopdf.com/ or 
https://md-to-pdf.fly.dev/


Here's a snippet of CSS that might help

```
/* Apply to the whole document */
body {
    font-family: 'Arial', sans-serif;  /* You can replace Arial with any preferred font */
    font-size: 16px;                   /* Base font size */
}

/* Apply different sizes to headers */
h1 {
    font-size: 32px;  /* Larger font size for H1 headers */
}

h2 {
    font-size: 24px;  /* Smaller than H1, but larger than normal text */
}

h3 {
    font-size: 20px;  /* H3 headers */
}

/* Paragraphs */
p {
    font-size: 16px;  /* Default size for paragraph text */
}

/* Apply to specific class */
.small-text {
    font-size: 12px;  /* You can create a class for smaller text */
}

.large-text {
    font-size: 24px;  /* Class for larger text */
}

/* Styling for blockquotes */
blockquote {
    font-size: 18px;                /* Slightly larger font for quotes */
    color: #333;                    /* Darker text color */
    background-color: #f0f0f0;      /* Light grey background highlight */
    padding: 10px 20px;             /* Padding around the text */
    margin: 20px 0;                 /* Space before and after the blockquote */
    border-left: 5px solid #ccc;    /* Grey border on the left for emphasis */
}

/* Optional italic style for blockquote text */
blockquote p {
    font-style: italic;
}

/* Table styling */
table {
    width: 100%;                  /* Full-width table */
    border-collapse: collapse;    /* Collapse borders to create single border lines */
    margin: 20px 0;               /* Add space above and below the table */
    font-size: 16px;              /* Base font size for table text */
    text-align: left;             /* Align text to the left */
    background-color: #f9f9f9;    /* Light grey background for the entire table */
}

/* Table header styling */
th {
    background-color: #4CAF50;    /* Header background in a nice green shade */
    color: white;                 /* White text for the header */
    padding: 12px 15px;           /* Padding for headers */
    border: 1px solid #ddd;       /* Light border around headers */
    font-size: 18px;              /* Larger font for headers */
}

/* Table data cell styling */
td {
    padding: 10px 15px;           /* Padding for table cells */
    border: 1px solid #ddd;       /* Light border around cells */
}

/* Alternating row background color for better readability */
tr:nth-child(even) {
    background-color: #f2f2f2;    /* Lighter background for even rows */
}

/* Hover effect on table rows */
tr:hover {
    background-color: #e0e0e0;    /* Light grey background on hover */
}

/* Styling for table caption */
caption {
    caption-side: bottom;         /* Place caption at the bottom of the table */
    padding: 10px;                /* Space around the caption */
    font-size: 14px;              /* Smaller font for the caption */
    color: #666;                  /* Grey text color for the caption */
}
```