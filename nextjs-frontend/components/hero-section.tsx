import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { InfiniteSlider } from '@/components/ui/infinite-slider'
import { ProgressiveBlur } from '@/components/ui/progressive-blur'
import { useTranslations } from 'next-intl'

export default function HeroSection() {
    const t = useTranslations('HomePage')

    return (
        <>
            <div className="overflow-x-hidden">
                <section>
                    <div className="pb-10 pt-8 md:pb-16 lg:pb-24 lg:pt-32">
                        <div className="relative mx-auto flex max-w-6xl flex-col px-6 lg:block">
                            <div className="mx-auto max-w-lg text-center lg:ml-0 lg:w-1/2 lg:text-left">
                                <h1 className="mt-8 max-w-md text-balance text-4xl font-medium md:text-5xl lg:mt-16 xl:text-6xl">{t('heroTitle')}</h1>
                                <p className="mt-8 max-w-2xl text-pretty text-lg">{t('heroDescription')}</p>

                                <div className="mt-12 flex flex-col items-center justify-center gap-2 sm:flex-row lg:justify-start">
                                    <Button
                                        asChild
                                        size="lg"
                                        className="px-5 text-base">
                                        <Link href="#features">
                                            <span className="text-nowrap">{t('heroExploreFeatures')}</span>
                                        </Link>
                                    </Button>
                                    <Button
                                        key={2}
                                        asChild
                                        size="lg"
                                        variant="ghost"
                                        className="px-5 text-base">
                                        <Link href="/jobs/new">
                                            <span className="text-nowrap">{t('heroRequestTrainingJob')}</span>
                                        </Link>
                                    </Button>
                                </div>
                            </div>
                            <Image
                                className="-z-10 order-first ml-auto h-56 w-full object-cover sm:h-96 lg:absolute lg:inset-0 lg:-right-20 lg:-top-96 lg:order-last lg:h-max lg:w-2/3 lg:object-contain filter"
                                src="/logo.svg"
                                alt="Abstract Object"
                                height="5000"
                                width="3000"
                            />
                        </div>
                    </div>
                </section>
                <section className="bg-background pb-8 md:pb-16">
                    <div className="group relative m-auto max-w-6xl px-6">
                        <div className="flex flex-col items-center md:flex-row">
                            <div className="md:max-w-44 md:border-r md:pr-6">
                                <p className="text-end text-sm">Technologies used for the Platform</p>
                            </div>
                            <div className="relative py-6 md:w-[calc(100%-11rem)]">
                                <InfiniteSlider
                                    speedOnHover={20}
                                    speed={40}
                                    gap={112}>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-5 w-fit grayscale dark:invert"
                                            src="https://html.tailus.io/blocks/customers/nvidia.svg"
                                            alt="Nvidia Logo"
                                            height="20"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-5 w-fit grayscale dark:invert"
                                            src="https://html.tailus.io/blocks/customers/github.svg"
                                            alt="GitHub Logo"
                                            height="16"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-15 w-fit grayscale dark:invert"
                                            src="/tensorflow.svg" // Updated to use absolute path
                                            alt="TensorFlow Logo"
                                            height="20"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-15 w-fit filter grayscale dark:invert"
                                            src="/celery.png" // Updated to use absolute path
                                            alt="Celery Logo"
                                            height="60"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-5 w-fit grayscale dark:invert"
                                            src="/fastapi.png" // Updated to use absolute path
                                            alt="FastAPI Logo"
                                            height="20"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-5 w-fit grayscale dark:invert"
                                            src="/next.svg" // Updated to use absolute path
                                            alt="Next.js Logo"
                                            height="20"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-6 w-fit grayscale dark:invert"
                                            src="/shadcn.png" // Updated to use absolute path
                                            alt="ShadCN Logo"
                                            height="30"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-6 w-fit grayscale dark:invert"
                                            src="/minio.png" // Updated to use absolute path
                                            alt="MinIO Logo"
                                            height="20"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-6 w-fit grayscale dark:invert"
                                            src="/mysql.svg" // Updated to use absolute path
                                            alt="MySQL Logo"
                                            height="30"
                                            width="auto"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <img
                                            className="mx-auto h-6 w-fit grayscale dark:invert"
                                            src="/docker.png" // Updated to use absolute path
                                            alt="Docker Logo"
                                            height="20"
                                            width="auto"
                                        />
                                    </div>
                                </InfiniteSlider>
                                <div className="bg-linear-to-r from-background absolute inset-y-0 left-0 w-20"></div>
                                <div className="bg-linear-to-l from-background absolute inset-y-0 right-0 w-20"></div>
                                <ProgressiveBlur
                                    className="pointer-events-none absolute left-0 top-0 h-full w-20"
                                    direction="left"
                                    blurIntensity={1}
                                />
                                <ProgressiveBlur
                                    className="pointer-events-none absolute right-0 top-0 h-full w-20"
                                    direction="right"
                                    blurIntensity={1}
                                />
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </>
    )
}
