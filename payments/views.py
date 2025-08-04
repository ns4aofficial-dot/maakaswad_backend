import razorpay
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Initialize Razorpay client using your Razorpay key and secret
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class CreateRazorpayOrder(APIView):
    """
    Creates a Razorpay Order from a given local Order ID and total amount.
    """

    def post(self, request):
        try:
            order_id = request.data.get('order_id')
            order = Order.objects.get(id=order_id)

            amount_in_paise = int(order.total_amount * 100)  # Razorpay expects amount in paise

            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1,
                'notes': {
                    'order_id': str(order.id),
                    'user': order.user.username
                }
            })

            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'amount': amount_in_paise,
                'currency': 'INR',
                'order_id': order.id
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyPayment(APIView):
    """
    Verifies Razorpay payment signature and updates order status.
    """

    def post(self, request):
        try:
            data = request.data
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            order_id = data.get('order_id')

            # Verifying signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)

            # Update order status to 'paid'
            order = Order.objects.get(id=order_id)
            order.status = 'paid'
            order.save()

            return Response({'message': 'Payment verified successfully', 'order_id': order.id}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
