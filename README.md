# elogate

Web app inspired by [elovation](https://github.com/elovation/elovation) to track
competitive games.

## Terminology

- Game: A type or category of game (i.e. 7 Wonders, Catan, Chess, Pool, etc.)
  - Tags: Searchable modifiers to a game, these may be things like specific game
    modes (8 Ball pool), or a specific event (Tournament).
- Match: A specific instance of a game played at some point in time. Each match
  can have an arbitrary number of tags for the defined game type. No tag
  structure will be enforced, users are responsible for applying sensible
  combinations of tags (i.e. it makes no sense for a match to be tagged both
  `8 Ball` and `9 Ball`, but `8 Ball` and `July 8 Ball tournament` would make
  sense)
- Player: A participant in a match
- User (admin): An authenticated individual authorized to create players, games,
  matches, etc.
  - Users are distinct from and not necessarily related to Players

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
  - Automatic score calculator?
    - Probably JSON column in database defining the score table schema per
      player + a special column allowing for custom final score calculation
- In addition to a per game ranking, there should probably be some notion of a
  rank per combination of tags. In might become really expensive to keep track
  of all the different combinations, but possibly the server can only update
  them when someone actually queries for their rank in that specific tag set?

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
- ~~Games and game modes can probably be stored in the same table with a foreign
  key for children/parent.~~ Tags will have a foreign key relation with games to
  define a list of valid modifiers to a base game
  - ~~For now, only one level of nesting is allowed (maybe enforced with a
    database rule or something). Game entries that have children can't have
    matches associated with it.~~
    - ~~Specifically, entries with children can't have parents, and entries with
      parents can't have children~~
    - ~~In practice you probably want at least 2 levels of nesting (Pool -> 8
      Ball -> Specific 8 Ball tournament), and at that point you may as well
      allow arbitrary nesting and leave it up to users to not abuse it.~~
  - Any time a match is created, admin can add arbitrary modifiers linked to the
    base game. Admin is responsible for ensuring the combination of tags is
    sane.
    - Might be nice to support default combinations or something
  - Any time a match is created, a player rank row is created for the base game
    by default.
    - Ranks for specific game types (set of tags) should also be supported.
      - For now maybe admin can specify valid sets to keep track of, possibly
        arbitrary sets can be allowed if we figure out some mechanism for lazily
        updating these custom sets
      - Ideally it would be nice to support some rich way of composing tags (i.e
        `matches with A or B but not C`), but for starters it will just be a
        list of foreign keys ANDed together.
