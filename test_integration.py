"""
Automated Integration Test Script for Finora Backend API
Tests the complete user journey from OTP to loan offers
"""

import httpx
import asyncio
import sys
from typing import Optional, Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
TEST_MOBILE = "9876543210"
TEST_NAME = "Test User"
TEST_EMAIL = "test@example.com"
TEST_LOAN_AMOUNT = 500000
TEST_LOAN_TYPE = "PERSONAL"
TEST_PAN = "ABCDE1234F"
TEST_AGE = 30
TEST_PINCODE = "110001"
TEST_EMPLOYMENT_TYPE = "Salaried"
TEST_MONTHLY_INCOME = 50000
TEST_INCOME_MODE = "Bank Account (NEFT/IMPS)"
TEST_CREDIT_SCORE_METHOD = "BUREAU"
TEST_CREDIT_SCORE = 750

# Global state
auth_token: Optional[str] = None
user_id: Optional[str] = None
application_id: Optional[str] = None


class TestResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.error = None
        self.response_data = None
        self.start_time = datetime.now()
        self.end_time = None

    def mark_passed(self, response_data: Any = None):
        self.passed = True
        self.response_data = response_data
        self.end_time = datetime.now()

    def mark_failed(self, error: str):
        self.passed = False
        self.error = error
        self.end_time = datetime.now()

    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


def print_header(text: str):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(result: TestResult):
    status = "✅ PASS" if result.passed else "❌ FAIL"
    duration = f"{result.duration():.2f}s"
    print(f"\n{status} - {result.test_name} ({duration})")
    if result.error:
        print(f"  Error: {result.error}")
    if result.response_data and isinstance(result.response_data, dict):
        print(f"  Response: {result.response_data}")


async def test_health_check() -> TestResult:
    result = TestResult("Health Check")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_send_otp() -> TestResult:
    global auth_token, user_id
    result = TestResult("Send OTP")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/auth/send-otp",
                json={"mobile": TEST_MOBILE}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_verify_otp() -> TestResult:
    global auth_token, user_id
    result = TestResult("Verify OTP")
    try:
        async with httpx.AsyncClient() as client:
            # First send OTP to get one in Redis
            await client.post(
                f"{API_BASE}/auth/send-otp",
                json={"mobile": TEST_MOBILE}
            )

            # Since we can't access Redis directly, we'll try a common OTP
            # In production, you'd need to mock the OTP service or extract from logs
            response = await client.post(
                f"{API_BASE}/auth/verify-otp",
                json={"mobile": TEST_MOBILE, "otp": "123456"}
            )

            # If OTP verification fails due to invalid OTP, that's expected in this test
            # We'll check if the endpoint is reachable
            if response.status_code in [200, 400]:
                if response.status_code == 200:
                    data = response.json()
                    auth_token = data.get("token")
                    user_id = data.get("user", {}).get("id")
                    result.mark_passed(data)
                else:
                    result.mark_failed("OTP verification failed (expected - need valid OTP)")
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_create_application() -> TestResult:
    global application_id
    result = TestResult("Create Loan Application")
    if not auth_token:
        result.mark_failed("No auth token available")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/loan-applications",
                json={
                    "loanType": TEST_LOAN_TYPE,
                    "name": TEST_NAME,
                    "email": TEST_EMAIL,
                    "loanAmount": TEST_LOAN_AMOUNT
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 201:
                data = response.json()
                application_id = data.get("applicationId")
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_save_kyc() -> TestResult:
    result = TestResult("Save KYC Details")
    if not auth_token or not application_id:
        result.mark_failed("Missing auth token or application ID")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_BASE}/loan-applications/{application_id}/kyc",
                json={
                    "pan": TEST_PAN,
                    "age": TEST_AGE,
                    "pincode": TEST_PINCODE
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_save_income() -> TestResult:
    result = TestResult("Save Income Details")
    if not auth_token or not application_id:
        result.mark_failed("Missing auth token or application ID")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_BASE}/loan-applications/{application_id}/income",
                json={
                    "employmentType": TEST_EMPLOYMENT_TYPE,
                    "monthlyIncome": TEST_MONTHLY_INCOME,
                    "incomeMode": TEST_INCOME_MODE
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_save_credit_score() -> TestResult:
    result = TestResult("Save Credit Score")
    if not auth_token or not application_id:
        result.mark_failed("Missing auth token or application ID")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_BASE}/loan-applications/{application_id}/credit-score",
                json={
                    "method": TEST_CREDIT_SCORE_METHOD,
                    "score": TEST_CREDIT_SCORE
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_get_application() -> TestResult:
    result = TestResult("Get Application Status")
    if not auth_token or not application_id:
        result.mark_failed("Missing auth token or application ID")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/loan-applications/{application_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_submit_application() -> TestResult:
    result = TestResult("Submit Application")
    if not auth_token or not application_id:
        result.mark_failed("Missing auth token or application ID")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/loan-applications/{application_id}/submit",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_get_offers() -> TestResult:
    result = TestResult("Get Loan Offers")
    if not auth_token or not application_id:
        result.mark_failed("Missing auth token or application ID")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/loan-applications/{applicationId}/offers",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_get_user_profile() -> TestResult:
    result = TestResult("Get User Profile")
    if not auth_token:
        result.mark_failed("No auth token available")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/users/me",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_get_dashboard() -> TestResult:
    result = TestResult("Get Dashboard")
    if not auth_token:
        result.mark_failed("No auth token available")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/dashboard",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_get_notifications() -> TestResult:
    result = TestResult("Get Notifications")
    if not auth_token:
        result.mark_failed("No auth token available")
        return result

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/notifications",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def test_get_faqs() -> TestResult:
    result = TestResult("Get FAQs")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/support/faqs")
            if response.status_code == 200:
                data = response.json()
                result.mark_passed(data)
            else:
                result.mark_failed(f"Status code: {response.status_code}, Body: {response.text}")
    except Exception as e:
        result.mark_failed(str(e))
    return result


async def main():
    print_header("Finora Backend Integration Test")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test Mobile: {TEST_MOBILE}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test 1: Health Check
    print_header("TEST 1: Infrastructure")
    result = await test_health_check()
    results.append(result)
    print_result(result)

    # Test 2: Auth Pipeline
    print_header("TEST 2: Authentication Pipeline")
    result = await test_send_otp()
    results.append(result)
    print_result(result)

    result = await test_verify_otp()
    results.append(result)
    print_result(result)

    # Test 3: User Profile
    print_header("TEST 3: User Profile")
    result = await test_get_user_profile()
    results.append(result)
    print_result(result)

    # Test 4: Multi-Step Application Funnel
    print_header("TEST 4: Multi-Step Application Funnel")
    result = await test_create_application()
    results.append(result)
    print_result(result)

    result = await test_save_kyc()
    results.append(result)
    print_result(result)

    result = await test_save_income()
    results.append(result)
    print_result(result)

    result = await test_save_credit_score()
    results.append(result)
    print_result(result)

    result = await test_get_application()
    results.append(result)
    print_result(result)

    # Test 5: Submission & Match Engine
    print_header("TEST 5: Submission & Match Engine")
    result = await test_submit_application()
    results.append(result)
    print_result(result)

    result = await test_get_offers()
    results.append(result)
    print_result(result)

    # Test 6: Dashboard & Support Services
    print_header("TEST 6: Dashboard & Support Services")
    result = await test_get_dashboard()
    results.append(result)
    print_result(result)

    result = await test_get_notifications()
    results.append(result)
    print_result(result)

    result = await test_get_faqs()
    results.append(result)
    print_result(result)

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    total_time = sum(r.duration() for r in results)

    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Total Duration: {total_time:.2f}s")
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")

    if failed > 0:
        print("\n❌ Failed Tests:")
        for r in results:
            if not r.passed:
                print(f"  - {r.test_name}: {r.error}")

    print("\n" + "=" * 70)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
