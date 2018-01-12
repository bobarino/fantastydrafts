# fantastydrafts
Code to optimize fantasy drafts (DraftKings)

Method 1

After failing to make a viable knapsack that took into account positional constraints, I decided to start off with a simpler approach of ordering the players based on point per dollar efficiency and finding the best combinations fulfilling positional requirements and cap spend requirements. I created many rosters after “popping” off the most efficient player every time in order to partially mitigate the problem of having a team with all high point efficiency, but not maximizing points and budget in the process (i.e. only spending $34,000 with highly efficient players, when theres plenty of room in the budget to get some large point players that may not be as efficient as they cost more). By creating these rosters, I then picked the roster with the largest sum of projected points, therefore partially taking into account point efficiency and an attempt to maximize potential points even if the player does not do it most efficiently.

Results (10/29/2017 Sunday Football NFL)

I was provided with a roster projecting 122.779 points at a budget of $44,300 with players ['Saints ', 'Carson Wentz', 'Charles Clay', 'Carlos Hyde', 'Ted Ginn Jr.', 'Lamar Miller', 'Michael Crabtree', 'DeAndre Hopkins’]. Upon submitting this roster, I found that Charles Clay was out and I forgot to add in a FLEX position, so I picked the FLEX and new TE manually (Danny Amendola and Jared Cook respectively). This left me with a roster projecting 131.866 points and a budget of $49,900. This roster placed me in 126,100 (out of 554,894, winnings up to position 149,250) and resulted in $5.00 of winnings ($5.00 profit as my first attempt was free).

Updates
10/26/2017

Fixed the FLEX issue, now the algorithm provides this roster: ['Saints ', 'Carson Wentz', 'Charles Clay', 'Jason Witten', 'Carlos Hyde', 'Ted Ginn Jr.', 'Lamar Miller', 'Michael Crabtree', 'DeAndre Hopkins’] (adds Jason Witten) with a budget of $48,500 and a projected 135.496 total points (as you can see, this beats my handpicked selection above). Still have the same problem with Charles Clay being out. I did not submit this roster and went with I’m looking into scraping ESPN data to fix this problem along with getting more player statistics.

10/30/2017

ESPN data is scraped with scrapy. I also moved from csv to a PostgreSQL database currently with 2 tables (DraftKings data and ESPN data). Will continue to optimize my roster algorithm with the additional data and more capabilities with the database.

11/01/2017

Factored the ESPN data into my algorithm. Right now, I just add the ESPN projected points of all players to their DraftKings average points per game, sort them based on the newly calculated points per dollar efficiency. I decided to use the projected points due to the fact that ESPN most likely has some very high-level math and analysis that is much more refined than what I can do in the short-term. With average points per game (taking into account the past) and week projections (taking into account mathematical analysis on the future), I can, in theory, create an even more optimized approach to picking the best roster (sequential AI). My new algorithm outputs the following roster: ['Deshaun Watson', 'Rams ', 'Jack Doyle', 'Carlos Hyde', 'Benjamin Watson', 'Todd Gurley II', 'Jeremy Maclin', 'J.J. Nelson', 'Will Fuller V', 45800, 254.33299999999997]

11/15/2017

Results (11/5/2017)- Ranked 3544/8045 (paying positions started at 3500) and 151642/495441 (paying positions started at 129200) with the roster Carson Wantz (24.76), Todd Gurley II (24.4), Carlos Hyde (21.5), Larry Fitzgerald (12), Jeremy Maclin (17.8), J.J. Nelson (2.5), Jack Doyle (14.3), Benjamin Watson (11.1), and Jagaurs (12). Due to a code error with my roster being created before scrapy fully ran on ESPN (fixed after this week with time delays in code), I added another roster with only partial ESPN data (just to see what would happen) which resulted in placing 117027/118906 (paying positions started at 29475) with Matt Ryan (22.42), Andre Ellington (3.4), Lamar Miller (12.1), Larry Fitzgerald (12), Will Fuller V (5.2), Marqise Lee (21.5), Jason Witten (1.5), Leonard Fournette (0), and Bengals (2).

Results (11/12/2017)- Ranked 15986/32699 (paying positions started at 7825) and 264591/535077 (paying positions started at 139650) with the roster Marcus Mariota (18.66), Todd Gurley II (19.6), Carlos Hyde (12.4), DeAndre Hopkins (21.1), Adam Humphries (3.7), Marqise Lee (19.5), Charles Clay (3.3), Devonta Freeman (0.3; Injured in the beginning of the 1st quarter), and Lions (14).

Results (11/14/2017; Sunday Night/Monday Games)- Ranked 157814/166468 (paying positions started at 40665) with Brock Osweiler (11.74), Devontae Booker (3.9), Christian McCaffrey (20), Brandin Cooks (13.4), Jarvis Landry (15.2), Kenny Stills (11.7), Ed Dickson (12.3), Rob Gronkowski (11.4), and Panthers (2)

Notes- Need to minimize the lowest scoring players (low single digit scores) and maximize players who sky rocket. To Do- Make ESPN data in sync with league rules. Create a new table comparing players performance to their projection (can do machine learning techniques on this to create a segmentation analysis of player's risk (low, medium, high)). Scrape other sources for more information.