import dayjs from 'dayjs'
import { useEffect, useRef, useState } from 'react'
import ProfileCard from './components/ProfileCard'
import RecordCard from './components/RecordCard'
import { Recording, User } from './types/tars'

const normalizeBaseUrl = (baseUrl: string) => baseUrl.replace(/\/+$/, '')

const buildApiUrl = (baseUrl: string, path: string) => {
  const normalizedBase = normalizeBaseUrl(baseUrl)
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${normalizedBase}${normalizedPath}`
}

const getRecordings = async (baseUrl: string) => {
  const response = await fetch(buildApiUrl(baseUrl, '/recordings'), { cache: 'no-store' })
  const data = await response.json()

  return data.recordings as Recording[]
}

const startRecording = async (baseUrl: string, screenId: string) => {
  const response = await fetch(buildApiUrl(baseUrl, `/recordings/${screenId}`), {
    method: 'POST'
  })
  const data = await response.json()

  return data as Recording
}

const stopRecording = async (baseUrl: string, screenId: string) => {
  const response = await fetch(buildApiUrl(baseUrl, `/recordings/${screenId}`), {
    method: 'DELETE'
  })

  const data = await response.json()

  return data
}

const getUsers = async (baseUrl: string) => {
  const response = await fetch(buildApiUrl(baseUrl, '/users'), { cache: 'no-store' })
  const data = await response.json()

  return data.users as User[]
}

const addUser = async (baseUrl: string, screenId: string) => {
  const response = await fetch(buildApiUrl(baseUrl, `/subscriptions/${screenId}`), {
    method: 'POST'
  })
  const data = await response.json()

  return data as User
}

const removeUser = async (baseUrl: string, screenId: string) => {
  const response = await fetch(buildApiUrl(baseUrl, `/subscriptions/${screenId}`), {
    method: 'DELETE'
  })

  const data = await response.json()

  return data as User
}

const extractScreenId = (input: string): string => {
  const trimmed = input.trim()
  const urlMatch = trimmed.match(/twitcasting\.tv\/([^/?#]+)/)
  if (urlMatch && urlMatch[1]) {
    return urlMatch[1]
  }
  return trimmed
}

export default function App() {
  const [recordings, setRecordings] = useState<Recording[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [refresh, setRefresh] = useState<boolean>(false)
  const [updateAt, setUpdateAt] = useState<string>('---')
  const [updateTimestamp, setUpdateTimestamp] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false)
  const [currentTime, setCurrentTime] = useState<number>(dayjs().unix())

  const recordingInputRef = useRef<HTMLInputElement>(null)
  const userInputRef = useRef<HTMLInputElement>(null)

  const intervalInputRef = useRef<HTMLInputElement>(null)
  const [intervalSec, setIntervalSec] = useState<number>(5)

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const shouldBeDark = savedTheme === 'dark' || (!savedTheme && prefersDark)

    setIsDarkMode(shouldBeDark)
    document.documentElement.classList.toggle('dark', shouldBeDark)
  }, [])

  const toggleDarkMode = () => {
    const newMode = !isDarkMode
    setIsDarkMode(newMode)
    document.documentElement.classList.toggle('dark', newMode)
    localStorage.setItem('theme', newMode ? 'dark' : 'light')
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(dayjs().unix())
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setRefresh(previous => !previous)
    }, intervalSec * 1000)

    return () => clearInterval(interval)
  }, [intervalSec])

  useEffect(() => {
    const resolvedBaseUrl = normalizeBaseUrl(window.location.origin)

    setIsLoading(true)

    Promise.all([getRecordings(resolvedBaseUrl), getUsers(resolvedBaseUrl)])
      .then(([recordingsData, usersData]) => {
        setRecordings(recordingsData)
        setUsers(usersData)
        const now = dayjs()
        setUpdateAt(now.format('YYYY/MM/DD HH:mm:ss'))
        setUpdateTimestamp(now.unix())
        setIsLoading(false)
      })
      .catch(() => {
        setIsLoading(false)
      })
  }, [refresh])

  const resolvedBaseUrl = normalizeBaseUrl(window.location.origin)

  const isUpdateDelayed =
    updateTimestamp !== null && currentTime - updateTimestamp > intervalSec * 2

  return (
    <main className='min-h-screen bg-gray-50 px-4 py-8 dark:bg-gray-900 md:px-10'>
      <div className='mx-auto mb-6 max-w-[1920px] px-8'>
        <div className='overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800'>
          <div className='border-b border-gray-100 bg-gradient-to-b from-gray-50 to-white px-6 py-2 dark:border-gray-700 dark:from-gray-800 dark:to-gray-800'>
            <div className='flex items-center justify-between'>
              <h3 className='text-base font-bold text-gray-900 dark:text-white'>設定</h3>
              <button
                onClick={toggleDarkMode}
                className='rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 transition-all hover:bg-gray-50 active:scale-95 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
                aria-label='ダークモード切り替え'
              >
                {isDarkMode ? '🌙' : '☀️'}
              </button>
            </div>
          </div>

          <div className='px-6 py-2'>
            <div className='flex flex-col items-start justify-between space-y-3 lg:flex-row lg:items-center lg:space-y-0'>
              <div className='flex flex-wrap items-center gap-2'>
                <label className='text-xs font-semibold text-gray-700 dark:text-gray-300'>
                  更新間隔
                </label>
                <div className='flex items-center space-x-1.5'>
                  <input
                    type='text'
                    ref={intervalInputRef}
                    defaultValue='5'
                    className='w-20 rounded-lg border border-gray-300 bg-gray-50 px-3 py-1.5 text-center text-sm outline-none transition-all focus:border-gray-400 focus:bg-white focus:ring-2 focus:ring-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-gray-500 dark:focus:bg-gray-600'
                  />
                  <span className='text-xs text-gray-500 dark:text-gray-400'>秒</span>
                </div>
                <button
                  className='rounded-lg bg-gray-700 px-4 py-1.5 text-sm font-medium text-white transition-all hover:bg-gray-800 active:scale-95 dark:bg-gray-600 dark:hover:bg-gray-700'
                  onClick={() => {
                    const data: number = Number(intervalInputRef.current?.value)
                      ? Number(intervalInputRef.current?.value)
                      : 30
                    setIntervalSec(data)
                  }}
                >
                  設定
                </button>
              </div>
              <div className='flex items-center space-x-2'>
                {isLoading && (
                  <div className='flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400'>
                    <svg className='h-3.5 w-3.5 animate-spin' fill='none' viewBox='0 0 24 24'>
                      <circle
                        className='opacity-25'
                        cx='12'
                        cy='12'
                        r='10'
                        stroke='currentColor'
                        strokeWidth='4'
                      ></circle>
                      <path
                        className='opacity-75'
                        fill='currentColor'
                        d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                      ></path>
                    </svg>
                    <span>更新中...</span>
                  </div>
                )}
                <div
                  className={`flex items-center space-x-1.5 rounded-full px-3 py-1.5 ${
                    isUpdateDelayed
                      ? 'bg-red-50 dark:bg-red-900/30'
                      : 'bg-green-50 dark:bg-green-900/30'
                  }`}
                >
                  <div
                    className={`h-1.5 w-1.5 animate-pulse rounded-full ${
                      isUpdateDelayed ? 'bg-red-500' : 'bg-green-500'
                    }`}
                  ></div>
                  <span className='text-xs font-medium text-gray-600 dark:text-gray-300'>
                    最終更新
                  </span>
                  <span
                    className={`text-xs font-semibold ${
                      isUpdateDelayed
                        ? 'text-red-700 dark:text-red-400'
                        : 'text-gray-900 dark:text-white'
                    }`}
                  >
                    {updateAt}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className='mx-auto mb-6 max-w-[1920px] px-8'>
        <div className='overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800'>
          <div className='bg-gradient-to-b from-gray-50 to-white px-6 py-3 dark:from-gray-800 dark:to-gray-800'>
            <div className='flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between'>
              <div className='flex items-center space-x-3'>
                <h3 className='text-lg font-bold text-gray-900 dark:text-white'>録画タスク</h3>
                <span className='rounded-full bg-red-600 px-3 py-1 text-sm font-bold text-white shadow-sm dark:bg-red-500'>
                  {recordings?.length}
                </span>
              </div>
              <div className='flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-x-2 sm:space-y-0'>
                <input
                  type='text'
                  ref={recordingInputRef}
                  placeholder='スクリーンID または URL を入力...'
                  className='rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm outline-none transition-all focus:border-gray-400 focus:ring-2 focus:ring-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-gray-500 sm:w-64'
                />
                <div className='flex space-x-2'>
                  <button
                    className='flex-1 rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-gray-800 active:scale-95 dark:bg-gray-600 dark:hover:bg-gray-700 sm:flex-none'
                    onClick={() => {
                      const value = recordingInputRef.current?.value
                      if (!value) {
                        return
                      }

                      const screenId = extractScreenId(value)
                      startRecording(resolvedBaseUrl, screenId).then(newRecording => {
                        setRecordings(prev => {
                          const exists = prev.find(r => r.live_id === newRecording.live_id)
                          if (exists) {
                            return prev.map(r =>
                              r.live_id === newRecording.live_id ? newRecording : r
                            )
                          }
                          return [...prev, newRecording]
                        })
                        if (recordingInputRef.current) {
                          recordingInputRef.current.value = ''
                        }
                      })
                    }}
                  >
                    開始
                  </button>
                  <button
                    className='flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-red-700 active:scale-95 dark:bg-red-500 dark:hover:bg-red-600 sm:flex-none'
                    onClick={() => {
                      const value = recordingInputRef.current?.value
                      if (!value) {
                        return
                      }

                      const screenId = extractScreenId(value)
                      stopRecording(resolvedBaseUrl, screenId).then(() => {
                        setRecordings(prev => prev.filter(r => r.screen_id !== screenId))
                        if (recordingInputRef.current) {
                          recordingInputRef.current.value = ''
                        }
                      })
                    }}
                  >
                    終了
                  </button>
                  <button
                    className='rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-all hover:bg-gray-50 active:scale-95 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
                    onClick={() => setRefresh(previous => !previous)}
                  >
                    更新
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className='mx-auto mb-6 max-w-[1920px] px-8'>
        <div className='grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-6 xl:grid-cols-5 2xl:grid-cols-6'>
          {recordings &&
            recordings.map(recording => (
              <RecordCard key={recording.live_id} recording={recording} />
            ))}
        </div>
      </div>

      <div className='mx-auto mb-6 max-w-[1920px] px-8'>
        <div className='overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800'>
          <div className='bg-gradient-to-b from-gray-50 to-white px-6 py-3 dark:from-gray-800 dark:to-gray-800'>
            <div className='flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between'>
              <div className='flex items-center space-x-3'>
                <h3 className='text-lg font-bold text-gray-900 dark:text-white'>登録ユーザー</h3>
                <span className='rounded-full bg-amber-600 px-3 py-1 text-sm font-bold text-white shadow-sm dark:bg-amber-500'>
                  {users?.length}
                </span>
              </div>
              <div className='flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-x-2 sm:space-y-0'>
                <input
                  type='text'
                  ref={userInputRef}
                  placeholder='スクリーンID または URL を入力...'
                  className='rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm outline-none transition-all focus:border-gray-400 focus:ring-2 focus:ring-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-gray-500 sm:w-64'
                />
                <div className='flex space-x-2'>
                  <button
                    className='flex-1 rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-gray-800 active:scale-95 dark:bg-gray-600 dark:hover:bg-gray-700 sm:flex-none'
                    onClick={() => {
                      const value = userInputRef.current?.value
                      if (!value) {
                        return
                      }

                      const screenId = extractScreenId(value)
                      addUser(resolvedBaseUrl, screenId).then(newUser => {
                        setUsers(prev => {
                          const exists = prev.find(u => u.user_id === newUser.user_id)
                          if (exists) {
                            return prev.map(u => (u.user_id === newUser.user_id ? newUser : u))
                          }
                          return [...prev, newUser]
                        })
                        if (userInputRef.current) {
                          userInputRef.current.value = ''
                        }
                      })
                    }}
                  >
                    追加
                  </button>
                  <button
                    className='flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-red-700 active:scale-95 dark:bg-red-500 dark:hover:bg-red-600 sm:flex-none'
                    onClick={() => {
                      const value = userInputRef.current?.value
                      if (!value) {
                        return
                      }

                      const screenId = extractScreenId(value)
                      removeUser(resolvedBaseUrl, screenId).then(() => {
                        setUsers(prev => prev.filter(u => u.screen_id !== screenId))
                        if (userInputRef.current) {
                          userInputRef.current.value = ''
                        }
                      })
                    }}
                  >
                    削除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className='mx-auto max-w-[1920px] px-8'>
        <div className='grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-6 xl:grid-cols-5 2xl:grid-cols-6'>
          {users &&
            users.map(user => {
              const isRecording = recordings?.some(r => r.screen_id === user.screen_id) ?? false
              return <ProfileCard key={user.user_id} user={user} isRecording={isRecording} />
            })}
        </div>
      </div>
    </main>
  )
}
