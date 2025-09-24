# elogate

Web app inspired by [elovation](https://github.com/elovation/elovation) to track
competitive games.

## Terminology

- Game: A type or category of game (i.e. 7 Wonders, Catan, Chess, etc.)
  - Game Mode: A specific rule set of a game. For example, you can't play a game
    of pool, you have to be playing with some specific rule set like 9 ball or 8
    ball.
- Match: A specific instance of a game played at some point in time
- Player: A participant in a match
- User (admin): An authenticated individual authorized to create players, games,
  matches, etc.
  - Users are distinct from Players

## Design Goals

- Reactive design (should look ok on narrow screens/mobile)
- Main page will show all games, admins will have buttons to create/delete games
- Players page will show all players, admins will have buttons to create/delete
  players
- Teams page will show all teams, admins will have buttons to create/delete
  teams
- Each team page will have a page showing team members
- Each player will have a page showing:
  - Current rank in all games they participate in
  - Recent matches
  - Graphs showing ranking progress for each game
- Each game will have a page showing:
  - Recent matches
  - Leader board showing current top players
  - Graph showing player rankings over time
  - Admins will be able to create/delete matches
    - If more than one participant on a side admin will have option to autosave
      that group to a team
    - Searchable dropdowns for players and teams for faster data entry
- Each match will have a page showing:
  - Participants and winners
  - Notes (nicegui rich text editor)
  - Attachments (picture of score cards etc.)
- Game modes should allow ranking per game mode and the overall game (i.e. a 9
  ball match would affect your 9 ball rank as well as an overall pool rank)

## Technical Design Choices

### Libs

- Frontend: nicegui
- Database: tortoiseorm (probably configurable but sqlite backed by default)
- Rating math: openskill

### Behaviors

- Admins should be able to retroactively create matches. The server should
  automatically recalculate all rankings necessary. Some heuristics to note:
  - Only matches after the added one need to be updated
    - If there are no newer matches containing the same players, no updates need
      to happen
- Games and game modes can probably be stored in the same table with a foreign
  key for children/parent.
  - For now, only one level of nesting is allowed (maybe enforced with a
    database rule or something). Game entries that have children can't have
    matches associated with it.
    - Specifically, entries with children can't have parents, and entries with
      parents can't have children
  - Any time a match is created, a player rank row is created for the game and
    parent game if exists.
    - This means the PlayerRank model will need a game foreign key ref to
      indicate the game being described
