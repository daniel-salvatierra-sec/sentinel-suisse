import { useEffect, useRef } from "react";

type Props = {
  enabled: boolean;
  loading: boolean;
  onVisible: () => void;
};

/** Fires `onVisible` when the sentinel enters the viewport (infinite scroll). */
export function InfiniteScrollSentinel({ enabled, loading, onVisible }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);
  const onVisibleRef = useRef(onVisible);
  onVisibleRef.current = onVisible;

  useEffect(() => {
    if (!enabled || loading) return;
    const node = ref.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          onVisibleRef.current();
        }
      },
      { root: null, rootMargin: "120px", threshold: 0 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [enabled, loading]);

  return <div ref={ref} className="scroll-sentinel" aria-hidden />;
}
