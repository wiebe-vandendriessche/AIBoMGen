import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Database, Layers, Settings2, ShieldCheck, Sparkles, Zap } from 'lucide-react'
import { ReactNode } from 'react'
import { useTranslations } from 'next-intl'

export default function Features() {
    const t = useTranslations('HomePage')

    return (
        <section id="features" className="py-16 md:py-32">
            <div className="@container mx-auto max-w-5xl px-6">
                <div className="text-center">
                    <h2 className="text-balance text-4xl font-semibold lg:text-5xl">{t('featuresTitle')}</h2>
                    <p className="mt-4">{t('featuresDescription')}</p>
                </div>
                <div className="@min-4xl:max-w-full @min-4xl:grid-cols-3 mx-auto mt-8 grid max-w-sm gap-6 [--color-background:var(--color-muted)] [--color-card:var(--color-muted)] *:text-center md:mt-16 dark:[--color-muted:var(--color-zinc-900)]">
                    <Card className="group bg-background">
                        <CardHeader className="pb-3">
                            <CardDecorator>
                                <ShieldCheck className="size-6" aria-hidden />
                            </CardDecorator>
                            <h3 className="mt-6 font-medium">{t('featureTrustabilityTitle')}</h3>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm">{t('featureTrustabilityDescription')}</p>
                        </CardContent>
                    </Card>

                    <Card className="group bg-background">
                        <CardHeader className="pb-3">
                            <CardDecorator>
                                <Database className="size-6" aria-hidden />
                            </CardDecorator>
                            <h3 className="mt-6 font-medium">{t('featureArtifactManagementTitle')}</h3>
                        </CardHeader>
                        <CardContent>
                            <p className="mt-3 text-sm">{t('featureArtifactManagementDescription')}</p>
                        </CardContent>
                    </Card>

                    <Card className="group bg-background">
                        <CardHeader className="pb-3">
                            <CardDecorator>
                                <Layers className="size-6" aria-hidden />
                            </CardDecorator>
                            <h3 className="mt-6 font-medium">{t('featureScalabilityTitle')}</h3>
                        </CardHeader>
                        <CardContent>
                            <p className="mt-3 text-sm">{t('featureScalabilityDescription')}</p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </section>
    )
}
const CardDecorator = ({ children }: { children: ReactNode }) => (
    <div className="relative mx-auto size-36 duration-200 [--color-border:color-mix(in_oklab,var(--color-zinc-950)10%,transparent)] group-hover:[--color-border:color-mix(in_oklab,var(--color-zinc-950)20%,transparent)] dark:[--color-border:color-mix(in_oklab,var(--color-white)15%,transparent)] dark:group-hover:bg-white/5 dark:group-hover:[--color-border:color-mix(in_oklab,var(--color-white)20%,transparent)]">
        <div aria-hidden className="absolute inset-0 bg-[linear-gradient(to_right,var(--color-border)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-border)_1px,transparent_1px)] bg-[size:24px_24px]" />
        <div aria-hidden className="bg-radial to-background absolute inset-0 from-transparent to-75%" />
        <div className="bg-background absolute inset-0 m-auto flex size-12 items-center justify-center border-l border-t">{children}</div>
    </div>
)
