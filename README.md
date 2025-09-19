# elogate

Web app inspired by [elovation](https://github.com/elovation/elovation) to track
competitive games.

## Terminology

- Game: A type or category of game (i.e. 7 Wonders, Catan, Chess, etc.)
- Match: A specific instance of a game played at some point in time
- Player: A participant in a match
- User (admin): An authenticated individual authorized to create players, games,
  matches, etc.
  - Users are distinct from Players

## Design Goals

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
