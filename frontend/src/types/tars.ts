export type Recording = {
  live_id: string
  screen_id: string
  user_name: string
  profile_image: string
  live_title: string
  live_subtitle: string
  start_time: number
}

export type User = {
  user_id: string
  screen_id: string
  user_name: string
  profile_image: string
  profile_description: string
  level: number
  supporter_count: number
  supporting_count: number
}
