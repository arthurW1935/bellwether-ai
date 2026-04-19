"use client";

import React, { useState } from 'react';
import { Button } from '@/components/common/Button';
import { Zap, Loader2 } from 'lucide-react';
import { trigger } from '@/lib/api';
import { Alert } from '@/lib/types';

interface TriggerButtonProps {
  onTriggered: (alert: Alert) => void;
  onError: (msg: string) => void;
}

export function TriggerButton({ onTriggered, onError }: TriggerButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const res = await trigger("exec_departure_demo_1");
      onTriggered(res.alert);
    } catch (err: unknown) {
      onError((err as Error).message || "Failed to trigger alert");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button variant="secondary" onClick={handleClick} disabled={loading}>
      {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2 text-violet-400" />}
      Simulate new signal
    </Button>
  );
}
