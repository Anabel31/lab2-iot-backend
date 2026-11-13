<?php
namespace Controllers;

require_once __DIR__ . '/../Repositories/EventRepository.php';

use Repositories\EventRepository;

class EventController {
    private EventRepository $events;

    public function __construct() {
        $this->events = new EventRepository();
    }

    public function index(): void {
        $data = $this->events->getAll();
        http_response_code(200);
        echo json_encode([
            'ok' => true,
            'data' => $data,
            'meta' => ['api_version' => 'v1']
        ]);
    }
}
