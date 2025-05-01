"""
This module contains all the preset queries for the sake of neatness and convenience
Mostly for internal usage
"""

mark_as_read_mutation = """
mutation{
  UpdateUser{
    unreadNotificationCount
  }
}
"""
reviews_query = """
query($id:Int){
  Page{
    pageInfo{
      total
    }
    reviews(mediaId:$id){
      summary
      user{
        name
        avatar {
          large
          medium
        }
      }
      body

    }
  }
}

"""
notification_query = """
query {
  Page(perPage: 5) {
    pageInfo {
      total
    }
    notifications(resetNotificationCount: true, type: AIRING) {
      ... on AiringNotification {
        id
        type
        episode
        contexts
        createdAt
        media {
          id
          idMal
          title {
            romaji
            english
          }
          coverImage {
            medium
          }
        }
      }
    }
  }
}
"""

get_medialist_item_query = """
query ($mediaId: Int) {
  MediaList(mediaId: $mediaId) {
    id
  }
}
"""

delete_list_entry_query = """
mutation ($id: Int) {
  DeleteMediaListEntry(id: $id) {
    deleted
  }
}
"""

get_logged_in_user_query = """
query{
  Viewer{
    id
    name
    bannerImage
    avatar {
      large
      medium
    }

  }
}
"""

get_user_info = """
query ($userId: Int) {
  User(id: $userId) {
    name
    about
    avatar {
      large
      medium
    }
    bannerImage
    statistics {
      anime {
        count
        minutesWatched
        episodesWatched
        genres {
          count
          meanScore
          genre
        }
        tags {
          tag {
            id
          }
          count
          meanScore
        }
      }
      manga {
        count
        meanScore
        chaptersRead
        volumesRead
        tags {
          count
          meanScore
        }
        genres {
          count
          meanScore
        }
      }
    }
    favourites {
      anime {
        nodes {
          title {
            romaji
            english
          }
        }
      }
      manga {
        nodes {
          title {
            romaji
            english
          }
        }
      }
    }
  }
}
"""
media_list_mutation = """
mutation (
  $mediaId: Int
  $scoreRaw: Int
  $repeat: Int
  $progress: Int
  $status: MediaListStatus
) {
  SaveMediaListEntry(
    mediaId: $mediaId
    scoreRaw: $scoreRaw
    progress: $progress
    repeat: $repeat
    status: $status
  ) {
    id
    status
    mediaId
    score
    progress
    repeat
    startedAt {
      year
      month
      day
    }
    completedAt {
      year
      month
      day
    }
  }
}
"""

media_list_query = """
query ($userId: Int, $status: MediaListStatus, $type: MediaType, $page: Int, $perPage: Int) {
  Page(perPage: $perPage, page: $page) {
    pageInfo {
      currentPage
      total
    }
    mediaList(userId: $userId, status: $status, type: $type) {
      mediaId
      media {
        id
        idMal
        title {
          romaji
          english
        }
        coverImage {
          medium
          large
        }
        trailer {
          site
          id
        }
        popularity
        streamingEpisodes {
          title
          thumbnail
        }
        favourites
        averageScore
        episodes
        genres
      synonyms
        studios {
          nodes {
            name
            isAnimationStudio
          }
        }
        tags {
          name
        }
        startDate {
          year
          month
          day
        }
        endDate {
          year
          month
          day
        }
        status
        description
        mediaListEntry {
          status
          id
          progress
        }
        nextAiringEpisode {
          timeUntilAiring
          airingAt
          episode
        }
      }
      status
      progress
      score
      repeat
      notes
      startedAt {
        year
        month
        day
      }
      completedAt {
        year
        month
        day
      }
      createdAt
    }
  }
}
"""


optional_variables = "\
$max_results:Int,\
$page:Int,\
$sort:[MediaSort],\
$id_in:[Int],\
$genre_in:[String],\
$genre_not_in:[String],\
$tag_in:[String],\
$tag_not_in:[String],\
$status_in:[MediaStatus],\
$status:MediaStatus,\
$status_not_in:[MediaStatus],\
$popularity_greater:Int,\
$popularity_lesser:Int,\
$averageScore_greater:Int,\
$averageScore_lesser:Int,\
$seasonYear:Int,\
$startDate_greater:FuzzyDateInt,\
$startDate_lesser:FuzzyDateInt,\
$startDate:FuzzyDateInt,\
$endDate_greater:FuzzyDateInt,\
$endDate_lesser:FuzzyDateInt,\
$format_in:[MediaFormat],\
$type:MediaType\
$season:MediaSeason\
$on_list:Boolean\
"

search_query = (
    """
query($query:String,%s){
  Page(perPage: $max_results, page: $page) {
    pageInfo {
      total
      currentPage
      hasNextPage
    }
    media(
      search: $query
      id_in: $id_in
      genre_in: $genre_in
      genre_not_in: $genre_not_in
      tag_in: $tag_in
      tag_not_in: $tag_not_in
      status_in: $status_in
      status: $status
      startDate: $startDate
      status_not_in: $status_not_in
      popularity_greater: $popularity_greater
      popularity_lesser: $popularity_lesser
      averageScore_greater: $averageScore_greater
      averageScore_lesser: $averageScore_lesser
      startDate_greater: $startDate_greater
      startDate_lesser: $startDate_lesser
      endDate_greater: $endDate_greater
      endDate_lesser: $endDate_lesser
      format_in: $format_in
      sort: $sort
      season: $season
      seasonYear: $seasonYear
      type: $type
        onList:$on_list
    ) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      mediaListEntry {
        status
        id
        progress
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }
      favourites
      averageScore
      episodes
      genres
      synonyms
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      description
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""
    % optional_variables
)

trending_query = """
query ($type: MediaType, $page: Int,$perPage:Int) {
  Page(perPage: $perPage, page: $page) {
    media(sort: TRENDING_DESC, type: $type, genre_not_in: ["hentai"]) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }
      favourites
      averageScore
      genres
      synonyms
      episodes
      description
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      mediaListEntry {
        status
        id
        progress
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

# mosts
most_favourite_query = """
query ($type: MediaType, $page: Int,$perPage:Int) {
  Page(perPage: $perPage, page: $page) {
    media(sort: FAVOURITES_DESC, type: $type, genre_not_in: ["hentai"]) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      mediaListEntry {
        status
        id
        progress
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }
      streamingEpisodes {
        title
        thumbnail
      }
      favourites
      averageScore
      episodes
      description
      genres
      synonyms
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

most_scored_query = """
query ($type: MediaType, $page: Int,$perPage:Int) {
  Page(perPage: $perPage, page: $page) {
    media(sort: SCORE_DESC, type: $type, genre_not_in: ["hentai"]) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      mediaListEntry {
        status
        id
        progress
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }
      episodes
      favourites
      averageScore
      description
      genres
      synonyms
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

most_popular_query = """
query ($type: MediaType, $page: Int,$perPage:Int) {
  Page(perPage: $perPage, page: $page) {
    media(sort: POPULARITY_DESC, type: $type, genre_not_in: ["hentai"]) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }
      favourites
      averageScore
      description
      episodes
      genres
      synonyms
      mediaListEntry {
        status
        id
        progress
      }
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

most_recently_updated_query = """
query ($type: MediaType, $page: Int,$perPage:Int) {
  Page(perPage: $perPage, page: $page) {
    media(
      sort: UPDATED_AT_DESC
      type: $type
      averageScore_greater: 50
      genre_not_in: ["hentai"]
      status: RELEASING
    ) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      mediaListEntry {
        status
        id
        progress
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }

      favourites
      averageScore
      description
      genres
      synonyms
      episodes
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

recommended_query = """
query ($mediaRecommendationId: Int, $page: Int) {
  Page(perPage: 50, page: $page) {
    recommendations(mediaRecommendationId: $mediaRecommendationId) {
      media {
        id
        idMal
        mediaListEntry {
          status
          id
          progress
        }
        title {
          english
          romaji
          native
        }
        coverImage {
          medium
          large
        }
        mediaListEntry {
          status
          id
          progress
        }
        description
        episodes
        trailer {
          site
          id
        }
        genres
        synonyms
        averageScore
        popularity
        streamingEpisodes {
          title
          thumbnail
        }
        favourites
        tags {
          name
        }
        startDate {
          year
          month
          day
        }
        endDate {
          year
          month
          day
        }
        status
        nextAiringEpisode {
          timeUntilAiring
          airingAt
          episode
        }
      }
    }
  }
}
"""


anime_characters_query = """
query ($id: Int, $type: MediaType) {
  Page {
    media(id: $id, type: $type) {
      characters {
        nodes {
          name {
            first
            middle
            last
            full
            native
          }
          image {
            medium
            large
          }
          description
          gender
          dateOfBirth {
            year
            month
            day
          }
          age
          bloodType
          favourites
        }
      }
    }
  }
}
"""


anime_relations_query = """
query ($id: Int) {
  Media(id: $id) {
    relations {
      nodes {
        id
        idMal
        type
        title {
          english
          romaji
          native
        }
        coverImage {
          medium
          large
        }
        mediaListEntry {
          status
          id
          progress
        }
        description
        episodes
        trailer {
          site
          id
        }
        genres
        synonyms
        averageScore
        popularity
        streamingEpisodes {
          title
          thumbnail
        }
        favourites
        tags {
          name
        }
        startDate {
          year
          month
          day
        }
        endDate {
          year
          month
          day
        }
        status
        nextAiringEpisode {
          timeUntilAiring
          airingAt
          episode
        }
      }
    }
  }
}
"""

airing_schedule_query = """
query ($id: Int,$type:MediaType) {
  Page {
    media(id: $id, sort: POPULARITY_DESC, type: $type) {
      airingSchedule(notYetAired:true){
        nodes{
          airingAt
          timeUntilAiring
          episode

        }
      }
    }
  }
}
"""

upcoming_anime_query = """
query ($page: Int, $type: MediaType,$perPage:Int) {
  Page(perPage: $perPage, page: $page) {
    pageInfo {
      total
      perPage
      currentPage
      hasNextPage
    }
    media(
      type: $type
      status: NOT_YET_RELEASED
      sort: POPULARITY_DESC
      genre_not_in: ["hentai"]
    ) {
      id
      idMal
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      mediaListEntry {
        status
        id
        progress
      }
      popularity
      streamingEpisodes {
        title
        thumbnail
      }
      favourites
      averageScore
      genres
      synonyms
      episodes
      description
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

anime_query = """
query ($id: Int) {
  Page {
    media(id: $id) {
      id
      idMal
      title {
        romaji
        english
      }
      mediaListEntry {
        status
        id
        progress
      }
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
      coverImage {
        extraLarge
      }
      characters(perPage: 5, sort: FAVOURITES_DESC) {
        edges {
          node {
            name {
              full
            }
            gender
            dateOfBirth {
              year
              month
              day
            }
            age
            image {
              medium
              large
            }
            description
          }
          voiceActors {
            name {
              full
            }
            image {
              medium
              large
            }
          }
        }
      }
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      season
      format
      status
      seasonYear
      description
      genres
      synonyms
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      duration
      countryOfOrigin
      averageScore
      popularity
      streamingEpisodes {
        title
        thumbnail
      }

      favourites
      source
      hashtag
      siteUrl
      tags {
        name
        rank
      }
      reviews(sort: SCORE_DESC, perPage: 3) {
        nodes {
          summary
          user {
            name
            avatar {
              medium
              large
            }
          }
        }
      }
      recommendations(sort: RATING_DESC, perPage: 10) {
        nodes {
          mediaRecommendation {
            title {
              romaji
              english
            }
          }
        }
      }
      relations {
        nodes {
          title {
            romaji
            english
            native
          }
        }
      }
      externalLinks {
        url
        site
        icon
      }
      rankings {
        rank
        context
      }
      bannerImage
      episodes
    }
  }
}
"""
