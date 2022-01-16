# A list of tuples containing configs for all the annual playlists
# Start date, end date, title in order
CREATED_PLAYLISTS = [('2012-01-00T12:00:00Z', '2013-06-25T17:59:59Z', 'JonTron Era - Game Grumps Chronology'),
                     ('2013-06-25T18:00:00Z', '2013-12-31T11:59:59Z', '2013 - Game Grumps Chronology'),
                     ('2014-01-00T12:00:00Z', '2014-12-31T11:59:59Z', '2014 - Game Grumps Chronology'),
                     ('2015-01-00T12:00:00Z', '2015-12-31T11:59:59Z', '2015 - Game Grumps Chronology'),
                     ('2016-01-00T12:00:00Z', '2016-12-31T11:59:59Z', '2016 - Game Grumps Chronology'),
                     ('2017-01-00T12:00:00Z', '2017-12-31T11:59:59Z', '2017 - Game Grumps Chronology'),
                     ('2018-01-00T12:00:00Z', '2018-12-31T11:59:59Z', '2018 - Game Grumps Chronology'),
                     ('2019-01-00T12:00:00Z', '2019-12-31T11:59:59Z', '2019 - Game Grumps Chronology'),
                     ('2020-01-00T12:00:00Z', '2020-12-31T11:59:59Z', '2020 - Game Grumps Chronology'),
                     ('2021-01-00T12:00:00Z', '2021-12-31T11:59:59Z', '2021 - Game Grumps Chronology'),
                     ('2022-01-00T12:00:00Z', '2022-12-31T11:59:59Z', '2022 - Game Grumps Chronology')
                     ]

# Playlists containing all uploads
UPLOADS_PLAYLISTS = [
    'UU9CuvdOVfMPvKCiwdGKL3cQ',  # Game Grumps
    'UUAQ0o3l-H3y_n56C3yJ9EHA'  # The Grumps
]

# These playlists should not be considered when deciding insertion order
SKIP_PLAYLISTS = {
    'FL9CuvdOVfMPvKCiwdGKL3cQ',  # Favorites
    'PLRQGRBgN_EnrsxaVTQJKIao6lDAJyYOw-',  # Game Grumps VS
    'PLRQGRBgN_EnrjPMktYLDYVwjwK-TXjimo',  # Game Grumps Starter Pack
    'PLRQGRBgN_EnrGIejPUT4H-oHJ0-_9K47A',  # Good Game
    'PLRQGRBgN_Enp8AlpQw7vGS0mEANb7ufIz',  # The G Club [Weekly Podcast]
    'PLRQGRBgN_EnpSqUheSWgweSMOcLdtI9w7',  # Game Grumps 10 Minute Power Hour
    'PLRQGRBgN_EnpsHKpbrow0ex8bOm8TXWej',  # GRUMPSWAVE Music
    'PLRQGRBgN_EnqizkZXJB4LP-af3Gum7Uhe',  # Commercials!!
    'PLRQGRBgN_EnqIWG6TuaGLWmn9NLcaHi7P',  # One Offs
    'PLRQGRBgN_Enq32ulNww6QJxdSp0cygD6m',  # Guest grumps
    'PLRQGRBgN_Enp7jEkUuzG5Z32gLY8-pPJl',  # Weird Bayonetta playlist with only one video that is private
    'PLRQGRBgN_EnqUyjIu3IxgrenDPTVOV_wM',  # SteamRolled
    'PLRQGRBgN_EnpND5AJknSiwwP9OKMYx4RP',  # Ghoul Grumps
    'PLRQGRBgN_EnrbKMOysGunwG4vdcmJwK8c',  # Second Undertale playlist
    'PLRQGRBgN_Enofh0M71j-c-JFuCM6Fpu7y',  # Livestreams
    'PLRQGRBgN_EnqU1NBgebcb6qP3YfYhmFi5',  # Reaction compilations
    'PLRQGRBgN_EnpvWVnEytLys8wLUHm5NSFh',  # Space Quest (game chronology)
    'PLRQGRBgN_Enq0QqqVJx8LDpNGdxlgEhO3',  # All monopoly series
    'PLRQGRBgN_EnqsgAMZkHdcQswhgYSqsptx',  # Mario party all series, there are a lot of dupe playlists
    'PLRQGRBgN_EnrjPMktYLDYVwjwK-TXjimo',  # Game grumps starter pack
    'PLRQGRBgN_Enr29rZZEzgSAQ21HjZXY0bv',  # Table Flip
    'PLRQGRBgN_EnoTAtMuaDjzjfuHvHVXXvZs',  # Mario party 10 dupe
    'PLRQGRBgN_EnocWoGhzsaXOgtlXhiX6LQC',  # Super Mega
    'PLRQGRBgN_EnqPmDxyt2_-GeEutC9RSpF6',  # Doodle Doods
    'PLRQGRBgN_EnqqwNutiWwAj8tZhMFIJ1rx',  # Jingle Grumps
    'PLRQGRBgN_EnpB6_L4ILekVICF_0kep4Kq',  # Mario Maker (both)
    'PLRQGRBgN_Enoz2CGGTgC3GqFoprgcsZFh',  # Wheel of Fortune
}

# These videos will go in as created instead of chunked together like most playlists
STRICT_CHRONO = {
    'PLRQGRBgN_Enp7Z8-nL2FPZh5XPX5xdBOH',  # Best of
    'PLRQGRBgN_EnrCbSE3UselKt4lupjneBjM',  # Game Grumps Compilations
    'PLC4E9F4F6136EF251',  # GG animated
    'PLRQGRBgN_EnrrO28pTREr_JJ8Hc9sLkjq',  # Soviet Jump Game
}

# These playlists are reversed
REVERSE_CHRON = {
    'PLRQGRBgN_Eno7t0cHrLVtqtgYp-tUv_t6',  # It Takes Two - playlist is backwards and has dupes?
    'PLRQGRBgN_EnrkKPf62css3lMrX6el6SGy',  # The Evil Within 2
}

# These playlists contain multiple series and should be split up when inserted
PLAYLIST_SPLITS = {
    'PLRQGRBgN_Enr363LeUKhGZUif_ctjcSly': ['2020-04-07T12:00:00Z'],  # Mario Party 2
    'PLRQGRBgN_EnqnzgNkK8uEc6TIw-WLH9WM': ['2015-11-20T00:00:00Z'],  # Mario Party 10
    'PLRQGRBgN_EnoPe_SXEf1Bxf8zur-Lpyum': ['2016-12-25T00:00:00Z', '2017-06-19T00:00:00Z', '2017-10-20T00:00:00Z',
                                           '2018-07-08T00:00:00Z'],  # Overwatch
    'PLRQGRBgN_EnqbmAguVJGpJuGx9NwP8ihN': ['2017-09-11T00:00:00Z'],  # Breath of the Wild
    'PLRQGRBgN_EnrpB12zm-Dydj_bgS1JEprm': ['2021-08-01T00:00:00Z'],  # Doki Doki
    'PLRQGRBgN_EnpI9GOH11qPpdTG4XByHrny': ['2020-05-14T00:00:00Z'],  # House Party
    'PLRQGRBgN_Enp8zHWw_UDHAHQ2ECVyiyM': ['2019-03-03T00:00:00Z'],  # Mario Bros U
    'PLRQGRBgN_Eno4h3d-LKBHSB7K89cWAC4f': ['2021-10-08T00:00:00Z', '2021-10-31T00:00:00Z'],  # Mario Maker
    'PLRQGRBgN_EnqDeCSYVQ3vNEcqVslLiq1d': ['2021-07-17T00:00:00Z'],  # Ace Attorney
    'PLRQGRBgN_Enokh3DN6ZsMrUNKu61kLsZI': ['2020-06-08T00:00:00Z'],  # Rocket League
    'PLRQGRBgN_EnrLiWt9O1rfLKEg_Eti3wrl': ['2020-07-05T00:00:00Z'],  # Super Bunny Man
    'PLRQGRBgN_Enq-ISJ_sgJdIntxvpyjGLAd': ['2021-10-24T00:00:00Z'],  # Phasmophobia
    'PLRQGRBgN_Enrt5T0-duFn_m-OEOsW63tb': ['2020-01-04T00:00:00Z'],  # Doom
    'PLRQGRBgN_EnqvJSkXAu4DI_tRQgbNwTEp': ['2017-11-16T00:00:00Z'],  # Stardew Valley
    'PLRQGRBgN_EnrULQN6IIjaMrKUUpyV08vK': ['2016-01-07T00:00:00Z', '2019-03-13T00:00:00Z', '2019-11-14T00:00:00Z'],
    # Undertale
    'PLRQGRBgN_EnrxtvIO8iQIuWItwFfkJ3Vk': ['2015-11-16T00:00:00Z', '2016-01-31T00:00:00Z', '2016-02-15T00:00:00Z',
                                           '2016-03-22T00:00:00Z', '2016-04-11T00:00:00Z', '2018-04-17T00:00:00Z'],
    # Mario Maker
    'PLRQGRBgN_EnpEKajx5RQiwaUQeh9uQL3g': ['2018-06-10T00:00:00Z'],  # Duck Game
    'PLRQGRBgN_EnoYweXHskEkO6PwgQmUF5HF': ['2017-07-31T00:00:00Z'],  # Super Mario 64
    'PLRQGRBgN_EnqR2L0BYORoMoJgMxSTIWTB': ['2018-10-23T00:00:00Z'],  # Punch Out
    'PLRQGRBgN_EnoM6ZoVt700eMUViWz4awFP': ['2019-06-23T00:00:00Z'],  # Wii Party U
    'PLRQGRBgN_EnpRvK_PKqehurc4k_RyYwGh': ['2014-01-23T00:00:00Z', '2015-07-21T00:00:00Z', '2018-09-18T00:00:00Z',
                                           '2020-09-04T00:00:00Z'],  # Ribbit King
    'PLRQGRBgN_Enq8ZiqD-7UDZe_zVmSfp8d9': ['2016-12-03T00:00:00', '2017-09-18T00:00:00', '2018-03-05T00:00:00',
                                           '2020-04-10T00:00:00'],  # Space Quest
    'PLRQGRBgN_Enp6Rvh3uUtOQ33DAq1mTiZN': ['2021-09-08T00:00:00'],  # Mario Party 6
    'PLRQGRBgN_EnqjoxISQFU5lcfHvgANpOMO': ['2020-11-15T00:00:00'],  # Mario Party 4
    'PLRQGRBgN_EnpMcjIlBPqWuFHyjNUJ1Qzy': ['2020-09-2200:00:00'],  # Monopoly vs Supermega
}

# These videos should not be included in any playlist
SKIP_VIDEOS = {

}

# Force videos that are out of order to be inserted correctly
# Each list should start with a video in the correct slot
FORCE_ORDER = {

}
