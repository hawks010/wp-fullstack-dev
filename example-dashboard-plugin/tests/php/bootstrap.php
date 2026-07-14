<?php
/**
 * PHPUnit bootstrap and minimal WordPress REST test doubles.
 *
 * @package MyAppDashboard
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

require_once dirname( __DIR__, 2 ) . '/vendor/autoload.php';

if ( ! class_exists( 'WP_REST_Request' ) ) {
	/**
	 * Minimal REST request test double.
	 */
	class WP_REST_Request {
		/** @var array<string, mixed> */
		private array $params;

		/** @var array<string, string> */
		private array $headers;

		/**
		 * Create a request double.
		 *
		 * @param array<string, mixed>  $params Request parameters.
		 * @param array<string, string> $headers Request headers.
		 */
		public function __construct( array $params = array(), array $headers = array() ) {
			$this->params  = $params;
			$this->headers = array_change_key_case( $headers, CASE_LOWER );
		}

		/**
		 * Return a request parameter.
		 *
		 * @param string $key Parameter key.
		 * @return mixed
		 */
		public function get_param( string $key ) {
			return $this->params[ $key ] ?? null;
		}

		/**
		 * Return a request header.
		 *
		 * @param string $key Header name.
		 * @return string|null
		 */
		public function get_header( string $key ): ?string {
			return $this->headers[ strtolower( $key ) ] ?? null;
		}
	}
}

if ( ! class_exists( 'WP_REST_Response' ) ) {
	/**
	 * Minimal REST response test double.
	 */
	class WP_REST_Response {
		/**
		 * Create a response double.
		 *
		 * @param mixed $data Response data.
		 * @param int   $status HTTP status.
		 */
		public function __construct( private $data = null, private int $status = 200 ) {}

		/** @return mixed */
		public function get_data() {
			return $this->data;
		}

		/** @return int */
		public function get_status(): int {
			return $this->status;
		}
	}
}

if ( ! class_exists( 'WP_Error' ) ) {
	/**
	 * Minimal WordPress error test double.
	 */
	class WP_Error {
		/**
		 * Create an error double.
		 *
		 * @param string $code Error code.
		 * @param string $message Error message.
		 * @param mixed  $data Error data.
		 */
		public function __construct( private string $code = '', private string $message = '', private $data = null ) {}

		/** @return string */
		public function get_error_code(): string {
			return $this->code;
		}

		/** @return mixed */
		public function get_error_data() {
			return $this->data;
		}
	}
}

if ( ! class_exists( 'WP_REST_Server' ) ) {
	/**
	 * REST method constants used by route registration.
	 */
	class WP_REST_Server {
		public const READABLE  = 'GET';
		public const CREATABLE = 'POST';
		public const DELETABLE = 'DELETE';
	}
}

WP_Mock::bootstrap();

require_once dirname( __DIR__, 2 ) . '/includes/class-rest-controller.php';
