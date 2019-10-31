# Hyphens and En Dashes and Em Dashes. Oh, my!

_or, How-To Input Dashes in the GNOME Desktop Environment_

### TL;DR (the cheat sheet)

- Hyphen (-): typed directly from keyboard  
- En dash (–): `[compose]`, then `[hyphen][hyphen][hyphen]`  
<span style="font-size: 75%;">_(i.e., `[compose]`, then `---`)_</span>  
- Em dash (—): `[compose]`, then `[hyphen][hyphen][period]`  
<span style="font-size: 75%;">_(i.e., `[compose]`, then `--.`)_</span>

### About Hyphens, En Dashes, and Em Dashes

Em dashes are approximately the width of the letter "M", en dashes the width of
the letter "N", and hyphens shorter still.

**Hyphens** are used to hyphenate a compound word: _merry-go-round_.

**En dashes** are not used as often, but are intended to be used for expressions
of range (time, numbers, etc.), most often as a replacement for the word "to",
and indicate the numbers are inclusive: _years 1900—2000, the New York—San
Francisco route, the score was 27—17._

**Em dashes** are used for two primary purposes: One, they are used to indicate
a stronger break in a sentence than a comma or a parenthesis. And two, they are
used similarly to how one would use a colon (but with a smidge more drama).

Em dashes in place of commas or parenthesis:  
_The 30th anniversary of the eruption of Mount St. Helens—May 18, 1980—brought
back vivid memories of ash and darkness._

Em dash in place of a colon:  
_There was only one thing missing from the pirate ship—pirates._

Read more about when to use hyphens, dashes, colons, parentheses&mdash;and
more&mdash;here:
- [Dashes, Colons, and Commas](https://www.quickanddirtytips.com/education/grammar/dashes-colons-and-commas)
- [Dashes, Parentheses, and Commas](https://www.quickanddirtytips.com/education/grammar/dashes-parentheses-and-commas)
- [Hyphens](https://www.quickanddirtytips.com/education/grammar/hyphens)
- [En Dash](https://www.thepunctuationguide.com/en-dash.html)
- [Em Dash](https://www.thepunctuationguide.com/em-dash.html)
- [Em Dash(—) vs. En Dash(–)](https://7esl.com/em-dash-en-dash/)

### The Problem

If you write more substantially than a short social-media post or informal
correspondence, you use hyphens and em dashes _all the time_. And sometimes,
perhaps, you even use en dash occasionally. The problem: There is no key on the
keyboard for the em or en dash. This can be maddening.

Inputting the hyphen on your keyboard is easy. The _minus-sign_ key on your
keyboard doubles as a hyphen key.

It should be noted that most people will just use hyphens in the place of en
dashes. Most editors will overlook this, but if you are writing more formally,
consider using the en dash instead.

### Dashes in Word Processors

Inputting the em dash in a word processor _can be_ relatively easy. Most will
replace any [-][-][space] with —. If your's doesn't, look for it in the settings
somewhere and enable it if you like. I personally like to input these characters
more directly from the keyboard. More on that in a second.

### Dashes in HTML- or Markdown-Formatted Documents

If you are creating an HTML- or markdown-formatted document, a common method to
input an em or en dash is to include `&mdash;` or `&ndash;` in the source text.
For example, this document was originally written in the Markdown format. I
generally prefer to input the dashes directly from the keyboard, but it is also
very common to input them as HTML `&` escape codes. It's very useful to know.

More about Markdown can be found
[here](https://en.wikipedia.org/wiki/Markdown),
[here](https://commonmark.org/help/), and
[here](https://www.markdownguide.org/extended-syntax).

More about HTML ASCII escape codes can be found
[here](https://ascii.cl/htmlcodes.htm). You can use HTML escape codes in
Markdown documents.

Markdown is widely used in many MANY programs now. Most note-taking
applications support it, some by default, or even nearly exclusively (example
[Joplin](https://joplinapp.org), my personal favorite). But also common forum
software ([Discourse](https://www.discourse.org/)). And many other platforms.

### Input of Dashes in the GNOME Desktop Environment

There are a myriad of ways to enable inputting of dashes in various operating
systems and desktop environments, but here I am going to describe how to do it
in GNOME, the default desktop environment for many favors of Linux, to include
Fedora, RHEL, and Ubuntu.

> For other environments (KDE and very old GNOME) take a look at the article
> referenced at the end of this section.

###### Compose Key Method

For these a _Compose Key_ is used. In Fedora's GNOME environment it is not
enabled by default. Or, at least, it was not on my desktop. To enable it, you
need to install the GNOME Tweak tool (it gives you more power over configuration
of the desktop).

**Install GNOME Tweak Tool**

Install from the UI:
- Open the "Software" application
- Search for "GNOME Tweaks"
- Install

Install from the commandline
- Fedora and EL8, RHEL8/CentOS8): `sudo dnf install gnome-tweaks -y`
- Ubuntu (I _believe_ this is correct): `sudo apt install gnome-tweak-tool`

**Enable and Map the Compose Key**

Now do this:
1. Open "Tweaks"
2. Select "Keyboard & Mouse"
3. Look for "Compose Key" and click on "Disabled"
4. Flip it from "OFF" to "ON"
5. Choose what you use for your compose key. I use "Caps Lock"  
   <span style="font-size: 75%;">_Note: whatever you choose, this setting will
   override any other use for that key._</span>

**Use the Compose Key**

Now open up a text editor (`gedit` will work, but any will do) and do this . . .

For an em dash (`[compose]`, then `---`), or
- `[compose key]` (in my case, the `[CAPS]` key)
- `[hyphen key]` (i.e., the minus sign)
- `[hyphen key]`
- `[hyphen key]`

  _You should now see an em dash (&mdash;)._

For an en dash (`[compose]`, then `--.`), or
- `[compose key]`
- `[hyphen key]`
- `[hyphen key]`
- `[period key]`

  _You should now see an en dash (&ndash;)._

###### Unicode Input Method

You can use the Unicode input method instead of using the compose key. It's a
bigger PITA and hard to remember, but, it is useful to know so you can input
other Unicode characters when necessary:

- `[CTRL][SHIFT][U]`

  _An underlined "<span style="text-decoration: underline">u</span>" should
  appear._

- The Unicode for the character needed
- `[ENTER]`  
  <span style="font-size: 75%;">_Note: the `[ENTER]` at the end may or may not
  be necessary, depending on the environment and application._</span>

For example:
- Hyphen (-): typed directly from keyboard.  
- En dash (–): `[CTRL][SHIFT][U]`, then `2013[ENTER]`
- Em dash (—): `[CTRL][SHIFT][U]`, then `2014[ENTER]`

A great summary of most if now all of the `[CTRL][SHIFT][U]` Unicode input codes
can be found in the "Diacritics and punctuation" section of this article: [Linux
keyboard text symbols: Compose key
shortcuts](https://fsymbols.com/keyboard/linux/compose/)

### How to Enable and Input Dashes in Other Environments

Are you a Microsoft or Apple user? That's beyond the scope of this document, but
here's a good starting point: [5 Ways to Type a
Dash](https://www.wikihow.com/Type-a-Dash).

That's it! Good luck and enjoy your writing.
