<?php

use Illuminate\Foundation\Application;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(using: static function (): void {
        require  __DIR__.'/../routes/web.php';
    })
    ->withExceptions()
    ->create();
