CREATE TABLE `requests` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`session` text NOT NULL,
	`instance` text NOT NULL,
	`scope_version` integer NOT NULL,
	`scope_id` text NOT NULL,
	`project_id` text NOT NULL,
	`name` text NOT NULL,
	`arguments` text NOT NULL,
	`call_id` text NOT NULL,
	`fingerprint` text NOT NULL,
	`status` text NOT NULL,
	`claim` text,
	`lease` integer,
	`created` integer NOT NULL,
	`expires` integer NOT NULL,
	`result` text
);
--> statement-breakpoint
CREATE UNIQUE INDEX `requests_idempotency` ON `requests` (`owner`,`session`,`call_id`);--> statement-breakpoint
CREATE INDEX `requests_queue` ON `requests` (`owner`,`session`,`status`,`created`);--> statement-breakpoint
CREATE TABLE `sessions` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`instance` text NOT NULL,
	`expires` integer NOT NULL,
	`heartbeat` integer NOT NULL,
	`revoked` integer DEFAULT 0 NOT NULL,
	`scope` text,
	`tools` text DEFAULT '[]' NOT NULL,
	`scope_version` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE INDEX `sessions_owner` ON `sessions` (`owner`,`expires`);